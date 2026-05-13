---
name: npm-publishing
description: 发布 npm 包到 npmjs.com。包含认证、权限、发布流程。
trigger: publish npm, 发布 npm 包, npm publish, create npm package
---

# npm Publishing

发布 npm 包到 npmjs.com。包含认证、权限、发布流程。

## 前置要求

### 1. npm 账号
- 账号: https://www.npmjs.com
- 需要 **Granular Access Token**（Classic Token 无法发布）
- Token 必须开启 **Bypass 2FA for `npm publish`** 权限

### 2. 包准备
```json
{
  "name": "your-package",
  "version": "1.0.0",
  "main": "dist/index.js",
  "bin": {
    "cli-name": "dist/cli.js"
  },
  "scripts": {
    "prepublishOnly": "npm run build"
  },
  "dependencies": {...},
  "engines": {
    "node": ">=18.0.0"
  },
  "files": ["dist", "README.md"]
}
```

**注意：** 将本地生成的文件（如 `license-keys.json`、`node_modules` 外的临时文件）加入 `.npmignore` 或 `files` 字段排除。发布前检查：
```bash
npm pack --dry-run  # 预览会包含哪些文件

## 认证流程

**步骤 1: 创建 .npmrc 文件**

在项目根目录创建 `.npmrc`：
```
//registry.npmjs.org/:_authToken=YOUR_NPM_TOKEN
```

**⚠️ 关键点：必须用 `.npmrc` 文件方式，`npm config set` 在某些环境下不生效。**

## ⚠️ npmrc 继承陷阱（关键！）

npm 配置是从全局 `~/.npmrc` 到项目 `.npmrc` **合并**的，不是覆盖。

**典型错误场景：**
```bash
# ~/.npmrc 内容：
registry=https://mirrors.tencentyun.com/npm
//registry.npmjs.org/:_authToken=npm_xxxxx  # 这是官方 registry 的 token！

# 项目 .npmrc 内容（你以为能覆盖）：
//registry.npmjs.org/:_authToken=npm_yyyyy
```

npm 会：**用 Tencent 镜像（来自全局） + 官方 registry 的 token（来自本地）** → 认证失败 `ENEEDAUTH`。

**解决方案（2选1）：**

**方案 A** — 在 `~/.npmrc` 统一设置：
```
registry=https://mirrors.tencentyun.com/npm
//mirrors.tencentyun.com/npm/:_authToken=YOUR_TENCENT_TOKEN
```

**方案 B** — 不用腾讯镜像，直接用官方 registry：
```
registry=https://registry.npmjs.org/
//registry.npmjs.org/:_authToken=YOUR_NPM_TOKEN
```

**调试命令：**
```bash
cat ~/.npmrc          # 查看全局配置
cat .npmrc            # 查看项目配置（如果有）
npm config list        # 查看合并后的有效配置
npm publish ... 2>&1 | grep -i auth  # 看是否是认证错误
```

### 3. 腾讯云镜像认证陷阱（最关键！）

**腾讯云镜像和 npmjs.org 需要分别认证，且 token 不同。**

```
# ~/.npmrc 通常是这样的（腾讯镜像 + npmjs token）：
registry=https://mirrors.tencentyun.com/npm
//registry.npmjs.org/:_authToken=npm_xxxxx   ← npmjs 的 token
//mirrors.tencentyun.com/npm/:_authToken=???  ← 腾讯镜像的 token（可能缺失）
```

**陷阱：** 当 `registry=https://mirrors.tencentyun.com/npm` 时，npm 发 publish 请求到腾讯镜像，但 auth token 是 `//registry.npmjs.org/` 下面的，腾讯镜像不认 → `ENEEDAUTH`。

**正确做法：腾讯镜像只读，发布用官方 registry。**

发布时永远显式指定官方 registry：
```bash
npm publish --access public --registry=https://registry.npmjs.org
```

临时完整覆盖 `~/.npmrc`：
```bash
# 写入正确的全局配置
cat > ~/.npmrc << 'EOF'
registry=https://registry.npmjs.org
//registry.npmjs.org/:_authToken=YOUR_NPM_TOKEN
EOF

npm publish --access public
# 完成后恢复原配置（如果还需用腾讯镜像）
```

**调试命令：**
```bash
npm config list            # 看实际生效的 registry 和 auth 配置
npm pack --dry-run          # 确认发布包含哪些文件
npm view <pkg> version      # 确认包已存在
```

**腾讯镜像发布失败特征：**
```
npm error code ENEEDAUTH
npm error need auth This command requires you to be logged in to https://mirrors.tencentyun.com/npm
```
→ 说明用了腾讯镜像但没配腾讯的 token，或腾讯镜像根本不支持发布。

### 4. 验证

```bash
npm view <package-name>
```

成功返回包信息即表示认证成功。

## 腾讯云镜像问题

如果使用腾讯云镜像，需要显式指定官方 registry：
```bash
npm publish --registry=https://registry.npmjs.org/
```

## 常见错误

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| `ENEEDAUTH` | 未登录/认证失败 | 检查 .npmrc 文件 |
| `E403 Forbidden` | Token 无发布权限 | 用 Granular Token，开启 Bypass 2FA |
| `E409 Conflict` | 版本号已存在 | `npm version minor && npm publish` 递增版本 |
| `E404 Not Found` | registry 配置错误或网络不通 | 确认 `--registry=https://registry.npmjs.org` 且网络可达 |

## 已发布版本冲突处理

npm 无法重复发布同一版本。若需更新已发布的包：

```bash
# 1. 检查当前版本
npm view <package-name> version

# 2. 递增版本号
npm version minor   # 1.0.0 → 1.1.0

# 3. 确认能读到包
npm view <package-name>

# 4. 发布
npm publish --registry=https://registry.npmjs.org/
```

## 更新发布

```bash
# 1. 更新版本号
npm version patch  # 1.0.0 -> 1.0.1

# 2. 重新发布
npm publish --registry=https://registry.npmjs.org/
```

## 参考

- `references/auth-setup.md` - 完整认证设置步骤