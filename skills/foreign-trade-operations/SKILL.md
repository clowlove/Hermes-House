---
name: foreign-trade-operations
description: >-
  Use this skill when managing a tractor/farm-machinery export business website.
  Covers: product listing creation, image optimization, SEO for international
  markets, search engine submission, and site maintenance workflows.
triggers:
  - "发布新产品"
  - "更新图片"
  - "SEO 优化"
  - "提交搜索引擎"
  - "外贸网站运营"
  - "tractor export"
---

# Foreign Trade Operations

## Website Overview

| Site | Platform | Domain | Canonical | Notes |
|------|----------|--------|----------|-------|
| 主站 | GitHub Pages + Cloudflare | shengtuo-tractor.com | → farm-implement.com | 已重定向 |
| 产品站 | GitHub Pages + Cloudflare | farm-implement.com | ✅ self | 主站，SEO 所有指向这里 |
| SADIN站 | GitHub Pages + Cloudflare | sadin-tractor.com | → farm-implement.com | 内容重复，通过 canonical 避免问题 |
| AIV站 | 本地服务器 + Cloudflare | aiv.qzz.io | ✅ self | 源码在 `/home/ubuntu/wwwroot/` |

**2026-05-18 SEO 优化完成:**
- farm-implement.com: canonical/sitemap/OG/JSON-LD 全部指向正式域名 ✅
- sadin-tractor.com: 通过 canonical 指向 farm-implement.com 避免重复内容
- aiv.qzz.io: 独立优化，添加完整 OGP/JSON-LD，源码本地

⚠️ **Cloudflare 覆盖 robots.txt**：Cloudflare Dashboard 的 Rules 可以覆盖源站 robots.txt。更新后不生效请检查 Cloudflare 设置。

**代码库：** `githubtalk/shengtuo-tractor`

### 重要：SEO canonical 指向

- **farm-implement.com** — 主站，所有 canonical/OG/sitemap 指向这里
- **sadin-tractor.com** — 内容相同，通过 canonical 避免重复内容问题
- **aiv.qzz.io** — 独立站，有自己的源码和 sitemap

> ⚠️ **GitHub Pages 部署需要 ~5分钟**，不是 1-2 分钟。推送后不能立即验证。

### 源文件路径

| 站点 | 源文件位置 | 部署方式 |
|------|-----------|----------|
| farm/sadin | `/home/ubuntu/shengtuo-tractor/` | GitHub Pages |
| aiv.qzz.io | `/home/ubuntu/wwwroot/` | FTP上传到 Windows 主机 |

---

## Product Listing Workflow

### 1. 准备产品图片

图片规范（参考 `compress-images.js`）：

```bash
# 压缩所有图片（已配置）
node compress-images.js

# 手动压缩单张（可选）
# - JPG: quality 75-80, progressive
# - PNG: compressionLevel 9
# - 最大尺寸: 1200x800px
# - 产品图建议: 800x600px
```

**命名规范：** `产品型号-角度-序号.jpg`
例：`ST904-侧面-1.jpg`、`MF904-正面-2.jpg`

### 2. 添加产品页面

产品页面存放路径：`/products/` 目录

每个产品页面需包含：
- 产品型号、名称（英文）
- 主要参数表格（发动机、功率、工作效率）
- 产品图片（带 alt 英文描述）
- PDF规格书下载链接（如有）
- 询盘按钮链接（mailto 或表单）

### 3. 更新 sitemap

生成 sitemap 后确保：
- 所有产品页面链接正确
- `lastmod` 更新为当天日期
- `priority` 按重要性：首页 1.0，产品列表 0.8，单品 0.6

---

## Image Optimization Script

路径：`/home/ubuntu/shengtuo-tractor/compress-images.js`

**用法：**
```bash
cd /home/ubuntu/shengtuo-tractor
node compress-images.js
```

**输出：** 报告压缩文件数 + 节省空间

---

## SEO Checklist

### 每次发布新产品后必做

- [ ] 产品标题含核心关键词（英文）
- [ ] 产品描述含长尾关键词（至少 3 处自然出现）
- [ ] 图片有 alt 英文描述
- [ ] sitemap 更新并提交
- [ ] Google Search Console 提交 URL
- [ ] Bing Webmaster 提交 URL
- [ ] Yandex Webmaster 提交 URL（如面向俄语市场）
- [ ] Baidu Webmaster 提交 URL（如面向中国市场）

### Meta Tags（各平台验证）

| 平台 | Tag | 位置 |
|------|-----|------|
| Google | `coJuNSF-ATVY_yxIm1lR6a4DphP3zTWYrzKABqat_Wg` | index.html |
| Baidu | `codeva-NbRNAmGaEy` (shengtuo-tractor.com) | index.html |
| Baidu | `codeva-1ecpfnMFSE` (farm-implement.com) | index.html |
| Yandex | `3fdba79f71c66d1b` | index.html |

---

## Search Engine Submission

### Google Search Console
URL: https://search.google.com/search-console
- 提交 sitemap: `https://www.shengtuo-tractor.com/sitemap.xml`
- 检测覆盖率错误
- 查看关键词排名

### Bing Webmaster
URL: https://www.bing.com/webmasters
- 需注册/登录 Microsoft 账户
- 支持扫码验证

### Yandex Webmaster
URL: https://webmaster.yandex.com
- 适合俄语、中亚、欧洲市场

### Baidu Webmaster
URL: https://ziyuan.baidu.com
- 中国市场必备
- 支持 HTML 文件验证或 Meta 标签验证

---

## SEO 优化标准流程（GitHub Pages）

当修改 GitHub Pages 站点时，所有 SEO 相关文件必须同步更新：

### 必须更新的 4 个文件

```bash
cd /home/ubuntu/shengtuo-tractor

# 1. index.html - canonical/OG/JSON-LD/sitemap/robots.txt
sed -i 's|old-domain|new-domain|g' index.html

# 2. categories.html（如有）
sed -i 's|old-domain|new-domain|g' categories.html

# 3. sitemap.xml
# 手动更新 <loc> 标签中的域名

# 4. robots.txt
# 更新 Sitemap 行
```

### GitHub Pages 部署流程

```bash
# 1. 修改文件
git add .
git commit -m "SEO update: canonical/OG/JSON-LD"

# 2. 推送到 GitHub（如有冲突）
git pull --rebase origin master
# 如有冲突：
# - 解决冲突
# - git add .
# - git rebase --skip  # 当无法设置 EDITOR 时用 skip

# 3. 推送
git push origin master

# 4. 等待 ~5 分钟生效
# 验证：curl https://raw.githubusercontent.com/USER/REPO/master/robots.txt
```

### AIV 站优化流程（本地服务器）

```bash
# 源文件在 /home/ubuntu/wwwroot/
# nginx root 已配置为 /home/ubuntu/wwwroot
# 修改后直接生效（无需上传）

# 更新包打包（需手动上传到其他服务器时）：
tar -czvf /tmp/aiv_seo_update.tar.gz index.html robots.txt sitemap.xml
```

### 域名绑定状态

- `shengtuo-tractor.com` → Cloudflare DNS，CNAME 指向源站
- `farm-implement.com` → GitHub Pages custom domain
- `sadin-tractor.com` → GitHub Pages custom domain（fork 仓库）

**注意：** GitHub Pages 如使用自定义域名，`Enforce HTTPS` 选项在 GitHub 后台可能不可点击（正常），由 Cloudflare 处理 HTTPS 跳转。

---

## 产品描述模板

英文产品描述结构（用于 SEO）：

```html
<!-- 产品标题 -->
<h1>[型号] Agricultural [产品类型] for Sale</h1>

<!-- 产品描述段落 -->
<p>The [型号] is a high-performance agricultural [产品类型] designed for
[主要应用场景]. Featuring [核心参数], it delivers reliable performance
in [适用地形/作物类型] operations across [目标市场].</p>

<!-- 参数列表 -->
<ul>
  <li><strong>Engine:</strong> [发动机型号]</li>
  <li><strong>Power:</strong> [功率] HP</li>
  <li><strong>Working Width:</strong> [工作宽度]</li>
  <li><strong>Application:</strong> [适用场景]</li>
</ul>

<!-- 关键词自然分布 -->
<p>This [产品类型] is ideal for [目标国家/地区] farmers looking for
cost-effective farming equipment. Competitive price, fast delivery,
and [其他卖点].</p>
```

---

## 市场关键词参考

| 市场 | 高频搜索词 |
|------|-----------|
| 东南亚 | tractor price, agricultural tractor, 4WD tractor |
| 非洲 | tractor for sale, farm equipment, affordable tractor |
| 欧洲 | agricultural machinery, farm tractor, CE certified |
| 南美 | tractor agrícola, equipo de granja, tractor económico |
| 中东 | farming equipment, agricultural implements |

---

## 常见问题

### 图片太大会影响加载速度
运行 `node compress-images.js` 批量压缩，建议单图 ≤ 200KB。

### sitemap 更新后搜索引擎没更新收录
手动到各平台 Search Console 提交 URL 或重新提交 sitemap，通常 3-7 天更新。

### Cloudflare HTTPS 525 错误
检查源站是否有有效 SSL 证书。无独立 IP 的共享主机建议使用 Cloudflare **Flexible SSL** 模式。

### Baidu 验证失败
确保验证文件正确上传到服务器根目录，或使用 Meta 标签验证方式（直接添加到 index.html 最优）。

---

## 工具路径速查

| 工具 | 路径 |
|------|------|
| 图片压缩脚本 | `/home/ubuntu/shengtuo-tractor/compress-images.js` |
| sitemap | `/home/ubuntu/shengtuo-tractor/sitemap.xml` |
| 主页 | `/home/ubuntu/shengtuo-tractor/index.html` |
| GitHub 仓库 | https://github.com/githubtalk/shengtuo-tractor |
| Cloudflare | https://dash.cloudflare.com |