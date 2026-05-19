# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue
2. Send details to: @talkcn (Telegram)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 24 hours
- **Initial Response**: Within 48 hours
- **Resolution**: ASAP depending on severity

## Security Best Practices

### API Keys
- Never commit API keys to repository
- Use environment variables
- Rotate keys regularly

### Dependencies
- Keep npm packages updated
- Review new dependencies
- Run `npm audit` regularly

### Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all connections
- Implement least privilege access

---

*Last Updated: 2026-05-17*