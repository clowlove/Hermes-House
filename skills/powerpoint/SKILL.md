---
name: powerpoint
description: "Create, read, edit .pptx decks, slides, notes, templates."
license: Proprietary. LICENSE.txt has complete terms
---

# Powerpoint Skill

## When to use

Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Chinese Aerospace** | `0A1628` (deep blue starfield) | `B80000` (Chinese red) | `E6B800` (gold) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |

**Chinese Aerospace theme** (used for 航天/space topics):
- Background: `#0A1628` (deep blue starfield)
- Primary: `#B80000` (Chinese red)
- Accent: `#E6B800` (gold)
- Text on dark: `#FFFFFF` / `#8899AA`
- Text on light: `#2D2D2D`
- Use for: 深蓝星空背景 + 中国红金色主题 presentations

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

### python-pptx on Hermes

**⚠️ Critical execution path** (verified 2026-05-18):

```bash
# WRONG — sandbox python3 (3.11) doesn't have pptx
python3 script.py   # ModuleNotFoundError: pptx

# WRONG — system python3 (3.12) also lacks pptx by default
/usr/bin/python3 script.py   # ModuleNotFoundError

# CORRECT — use hermes-agent venv python with uv-installed pptx
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 /tmp/script.py

# Installation
uv pip install python-pptx   # installs into hermes-agent venv

# Verify
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -c "from pptx import Presentation; print('ok')"
```

**Key insight**: `execute_code` tool uses sandboxed Python without pptx. Use `terminal` with the venv python path.

- `execute_code` tool → sandboxed Python (no pptx available)
- `terminal` with `/usr/bin/python3` → system Python 3.12 (pptx works)
- `pip install` needs `--break-system-packages` on externally-managed environments

### Content Verification Workflow (for factual content)

When creating presentations with real-world data (航天, 时事, 科技, etc.), always verify against authoritative sources:

**Step 1: Extract verification targets**
- Identify claims needing verification (dates, numbers, names, technical specs)

**Step 2: Search authoritative sources**
```bash
# Preferred sources (in order):
# 1. 澎湃新闻 (thepaper.cn) — 中国领先媒体
# 2. 央视新闻 (cctv.com)
# 3. 新华视点 (xinhuanet.com)
# 4. 人民日报

# Use trendradar for searches
mcp_trendradar_search_news(query="神舟二十三号 发射", limit=5, include_url=true)
```

**Step 3: Correct and annotate**
- Update data in script with verified values
- Add inline annotation like `[已核实]` or `[来源：澎湃新闻 2026-05-16]`
- Preserve original text style/format — don't rephrase user's phrasing

**Step 4: Generate corrected version**
- Re-run script with verified data
- Send to user with summary of corrections

### Format Preservation (docx/pptx)

When user says **"格式保持不变"** or similar:
- Only correct verifiable factual errors (wrong dates, numbers, names)
- Do NOT rewrite, rephrase, or restructure user's content
- Keep original text style, paragraph breaks, bullet structure
- Add corrections inline with minimal markers like `[已核实]` or `[修正]`
- Preserve all original formatting (fonts, colors, spacing)

**What to fix vs. preserve:**
| Fix | Preserve |
|-----|----------|
| Wrong dates/numbers | Original phrasing |
| Incorrect names | Paragraph structure |
| Verifiable factual errors | Bullet style |
| Outdated statistics (with source) | Section order |

### PPT + docx Decision Tree

- `pip install "markitdown[pptx]"` - text extraction
- `pip install python-pptx --break-system-packages` - creating from Python
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch (Node.js alternative)
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
