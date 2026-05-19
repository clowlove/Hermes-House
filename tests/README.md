# Test Suite

> Keep Hermès Agent reliable with automated tests

## Structure

```
tests/
├── skills/          # Skill-specific tests
├── core/            # Core functionality tests
├── integration/     # Service integration tests
└── fixtures/        # Test data
```

## Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific suite
npm test -- --grep "trendradar"
```

## Writing Tests

```javascript
describe('Skill: trendradar', () => {
  it('should fetch latest news', async () => {
    const result = await skill.execute({ action: 'latest' });
    expect(result).toHaveProperty('news');
  });
});
```

## CI Integration

Tests run automatically on:
- Every PR to `main`
- Every push to `develop`

---

*Status: TODO - Test suite to be implemented*

Last Updated: 2026-05-17