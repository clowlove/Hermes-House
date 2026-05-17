# Schema Markup Generator

Generate JSON-LD structured data for rich snippets and AI search enhancement.

## When This Skill Triggers

- "structured data", "JSON-LD", "schema markup"
- "rich snippets", "rich results"
- "FAQ schema", "Product schema", "HowTo schema"
- "add schema to my site", "schema.org"
- "Product structured data", "Organization schema"

## What This Skill Does

1. **FAQ Schema** — Q&A content for rich snippets
2. **Product Schema** — E-commerce product data (price, availability, reviews)
3. **HowTo Schema** — Step-by-step instructions
4. **Organization Schema** — Company information
5. **Breadcrumb Schema** — Navigation path
6. **Local Business Schema** — For location-based businesses

## Quick Start

```
Add FAQ schema to our product pages
```

```
Create Product schema for our tractor listings
```

```
Add structured data for a how-to guide page
```

## Common Schema Types

| Schema Type | Use Case |
|-------------|----------|
| FAQPage | Q&A content, support pages |
| Product | E-commerce products |
| HowTo | Step-by-step guides |
| Organization | Company info |
| LocalBusiness | Store locations |
| BreadcrumbList | Navigation trails |
| Article | Blog posts, news |
| Video | Video content |

## Example: FAQ Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What tractors do you export?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "We export 25-180HP tractors..."
    }
  }]
}
```

## Validation

- Use Google's Rich Results Test: https://search.google.com/test/rich-results
- Use Schema.org Validator: https://validator.schema.org/

## Reference

Original TopRank implementation: `seo/schema-markup-generator/SKILL.md`