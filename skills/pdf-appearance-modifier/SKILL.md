---
name: pdf-appearance-modifier
description: "Modify PDF appearance without changing content/structure: change font colors, remove highlights, adjust styling. Preserves all text, layout, fonts, and embedded resources."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, pikepdf, color-modification, appearance]
    related_skills: [ocr-and-documents, nano-pdf]
---

# PDF Appearance Modifier

For tasks like changing red font to black, removing highlights, or adjusting visual styling while keeping document content and structure 100% intact.

## Trigger

User asks to change font colors, remove highlights, or modify visual styling in a PDF without altering content, layout, or formatting.

## Critical Pitfall: PyMuPDF `span["color"]` is read-only

**Never try to mutate `span["color"]` in PyMuPDF (`fitz`).** Span properties are read-only views. Assignments silently fail — the color reverts when saving.

```python
# ❌ This does NOT work:
for span in page.get_text("dict")["blocks"][...]:
    span["color"] = (0, 0, 0)  # silently ignored
```

## Worked Approach: Stream-level surgery with `pikepdf`

### Step 1: Identify the color operator

PDF text color is set via graphics operators in page content streams:

| Operator | Colorspace | Example |
|----------|-----------|---------|
| `scn` | Current colorspace (often `/srgb`) | `0.918 0.471 0.471 scn` |
| `rg` / `RG` | DeviceRGB | `0.918 0.471 0.471 rg` |
| `g` / `G` | DeviceGray | `0.5 g` |

**Discovery tip**: Use `pikepdf` to iterate page streams and print lines containing `scn`, `rg`, `g`, etc. with their context.

### Step 2: Decode the stream

Content streams are often FlateDecode-compressed. With `pikepdf`:

```python
import pikepdf

pdf = pikepdf.open("input.pdf")
page = pdf.pages[0]

for stream in pikepdf.Array(page.Contents):
    data = stream.read_bytes().decode('latin-1', errors='replace')
    # data may already be decompressed by pikepdf
```

### Step 3: Replace color values

Use regex with a tolerance window so small floating-point variations don't slip through:

```python
import re

scn_pattern = re.compile(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+scn')

def replace_red(m):
    r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
    if r > 0.7 and r > g + 0.1 and r > b + 0.1:
        return '0 0 0 scn'
    return m.group(0)

new_text = scn_pattern.sub(replace_red, text)
```

### Step 4: Rebuild and preserve filters

```python
new_stream = pikepdf.Stream(pdf, new_text.encode('latin-1'))

# Preserve compression filter if present
if '/Filter' in stream.obj:
    new_stream['/Filter'] = stream['/Filter']

page.Contents = pikepdf.Array(new_streams)
```

### Step 5: Verify

Reopen with `pymupdf` and check `span["color"]` across all pages. Old red spans should now report the new color integer.

```python
import fitz
doc = fitz.open("output.pdf")
for page in doc:
    for span in page.get_text("dict")["blocks"]:
        c = span.get("color")
        # old red was (234, 120, 120) -> int 15366264
```

## Why `pikepdf` instead of PyMuPDF

PyMuPDF sanitizes invalid ICC colorspaces when inserting new content, which can corrupt documents with embedded color profiles. `pikepdf` performs minimal surgery on existing streams, preserving the original document structure, fonts, and embedded resources.

## Pitfalls and Corrections

### 1. `page.Contents` is polymorphic — handle both single Stream and Array

```python
# ❌ Assumes Array:
for stream in page.Contents:
    ...

# ✅ Handle both cases:
from pikepdf import Array

if isinstance(page.Contents, Array):
    streams = list(page.Contents)
else:
    streams = [page.Contents]
```

### 2. Stream property access — use dict syntax, not `.obj`

```python
# ❌ This fails:
if '/Filter' in stream.obj:

# ✅ Use stream as a mapping:
if '/Filter' in stream:
    new_stream['/Filter'] = stream['/Filter']
```

### 3. `pikepdf.Stream()` constructor signature

```python
# ✅ Correct:
new_stream = pikepdf.Stream(pdf, data.encode('latin-1'))

# ❌ Wrong (extra args or wrong order):
new_stream = pikepdf.Stream(pdf, new_text.encode('latin-1'))  # correct
```

### 4. Verify with PyMuPDF after pikepdf save

After saving, reopen with `fitz` and inspect `span["color"]` to confirm replacements landed. Old red (e.g. `0.918 0.471 0.471` = int `15366264`) should be gone.

```python
import fitz
doc = fitz.open("output.pdf")
for page in doc:
    for block in page.get_text("dict")["blocks"]:
        for span in block.get("lines", []):
            c = span.get("color")
            if c == 15366264:
                print("RED STILL PRESENT!")
doc.close()
```

## When to Use This vs Other Tools

| Tool | Use Case |
|------|---------|
| `nano-pdf` | Edit text content, typos, titles via NL prompts |
| `ocr-and-documents` | Extract text from PDFs (pymupdf, marker-pdf) |
| **This skill** | Modify visual styling (colors, highlights) without touching content |
| `python-pptx` / `powerpoint` skill | PowerPoint files |

## Example: Batch change red text to black across multiple PDFs

```python
import os, re, pikepdf

input_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
output_dir = "./redacted"
os.makedirs(output_dir, exist_ok=True)

scn_pattern = re.compile(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+scn')

for path in input_files:
    pdf = pikepdf.open(path)
    for page in pdf.pages:
        contents = page.Contents
        streams = [contents] if hasattr(contents, 'read_bytes') else list(contents)
        new_streams = []
        for stream in streams:
            if not hasattr(stream, 'read_bytes'):
                new_streams.append(stream)
                continue
            data = stream.read_bytes().decode('latin-1', errors='replace')
            original = data
            data = scn_pattern.sub(replace_red, data)
            if data != original:
                new_stream = pikepdf.Stream(pdf, data.encode('latin-1'))
                if '/Filter' in stream:
                    new_stream['/Filter'] = stream['/Filter']
                new_streams.append(new_stream)
            else:
                new_streams.append(stream)
        page.Contents = pikepdf.Array(new_streams)
    
    out_path = os.path.join(output_dir, os.path.basename(path))
    pdf.save(out_path)
    pdf.close()
```
