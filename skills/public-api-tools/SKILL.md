---
name: public-api-tools
description: 来自 public-apis 项目的免费公共 API 工具集 — QR码、图标、截图、LaTeX公式渲染等
triggers:
  - "生成二维码"
  - "QR code"
  - "qrcode"
  - "获取网站图标"
  - "favicon"
  - "截图"
  - "screenshot"
  - "LaTeX 公式"
  - "latex"
  - "公式渲染"
---

# Public API Tools

整合自 [public-apis](https://github.com/public-apis/public-apis) 项目的免费公共 API。

## QR Code 生成

### 1. goqr.me (推荐 - 免费无需 API Key)
```bash
curl -s "http://api.qrserver.com/v1/create-qr-code/?size=300x300&data=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$url'))")" -o qr.png
```
- 官方文档: https://goqr.me/api/

### 2. Image-Charts (免费无需 API Key)
```bash
curl -s "https://image-charts.com/chart?chs=300x300&cht=qr&chl=${encoded_url}&choe=UTF-8" -o qr.png
```
- 支持自定义尺寸和颜色

### 3. QR Code Monkey (支持 Logo)
```bash
curl -s "https://api.qrcode-monkey.com/qr/custom?data=${encoded_url}&size=300&download=0" -o qr.png
```

## 网站 Favicon 获取

### 1. 直接获取 favicon.ico (推荐)
```bash
curl -sL "https://{domain}/favicon.ico" -o favicon.png
```
示例: `curl -sL "https://github.com/favicon.ico" -o favicon.png`

### 2. DuckDuckGo Icons API (备选)
```bash
curl -sL "https://icons.duckduckgo.com/ip3/{domain}.ico" -o favicon.png
```
示例: `curl -sL "https://icons.duckduckgo.com/ip3/github.com.ico" -o favicon.png`

## LaTeX 公式渲染

### CodeCogs
```bash
curl -s "https://latex.codecogs.com/png.latex?${encoded_latex}" -o formula.png
```
示例: `\int_{0}^{1} x^2 dx`

## 图表生成

### Image-Charts (折线图、柱状图、饼图等)
```
https://image-charts.com/chart?chs=400x300&cht=lc&chd=s:hello&chan
```

## 需要 API Key 的服务 (供参考)

### PDF 生成
- **Html2Pdf.app**: https://html2pdf.app/ (免费额度 100 credits/月)
- **pdflayer** (apilayer): https://pdflayer.com/

### 截图
- **Screenshotlayer**: https://screenshotlayer.com/
- **AbstractAPI Screenshots**: https://www.abstractapi.com/website-screenshot-api

### Email 验证
- **Mailboxlayer**: https://mailboxlayer.com/
- **AbstractAPI Email**: https://www.abstractapi.com/email-verification-validation-api

## 使用示例

```python
import urllib.parse
import subprocess

def generate_qr(url, output="qr.png"):
    encoded = urllib.parse.quote(url)
    cmd = f'curl -s "https://image-charts.com/chart?chs=300x300&cht=qr&chl={encoded}&choe=UTF-8" -o {output}'
    subprocess.run(cmd, shell=True)
    return output

def get_favicon(domain, output="favicon.png"):
    cmd = f'curl -s "https://icon.horse/{domain}" -o {output}'
    subprocess.run(cmd, shell=True)
    return output
```