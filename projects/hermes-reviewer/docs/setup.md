# Hermès Reviewer - Setup Guide

## Prerequisites

- Node.js 18+
- A server with a public URL (for webhooks)
- GitHub App credentials

## Environment Setup

Create a `.env` file:

```bash
# GitHub App credentials
GITHUB_APP_ID=123456
GH_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
WEBHOOK_SECRET=your_webhook_secret
INSTALLATION_ID=1234567

# AI Model (NVIDIA NIM example)
MODEL_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_API_KEY=your_nvidia_api_key

# Server
PORT=3000
```

## Local Development

```bash
# Install
npm install

# Start server
npm start

# Use ngrok for webhook testing
ngrok http 3000
```

## Testing

```bash
# Send a test webhook
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d @test/fixtures/pr_opened.json
```

## Deploying

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY src/ ./src/
CMD ["npm", "start"]
```

### Railway / Render / Heroku

Set environment variables in the dashboard and deploy.

## Troubleshooting

1. **App not responding to webhooks**
   - Check webhook URL is publicly accessible
   - Verify GitHub App permissions
   - Check server logs for errors

2. **AI review failing**
   - Verify MODEL_BASE_URL and MODEL_API_KEY
   - Check AI API rate limits

3. **Permission denied**
   - Ensure GitHub App has pull_request write permission
   - Re-install the app on affected repositories