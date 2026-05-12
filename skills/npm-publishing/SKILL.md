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
  }
}
```

## 认证流程

**步骤 1: 创建 .npmrc 文件**

在项目根目录创建 `.npmrc`：
```
//registry.npmjs.org/:_authToken=YOUR_NPM_TOKEN
```

**⚠️ 关键点：必须用 `.npmrc` 文件方式，`npm config set` 在某些环境下不生效。**

**步骤 2: 验证 token 权限**

```bash
npm view <package-name>  # 测试读权限
```

## 发布命令

```bash
cd /path/to/project

# 发布公开包
npm publish --access public --registry=https://registry.npmjs.org/
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