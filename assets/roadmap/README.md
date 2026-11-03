# ProsperoCraft roadmap artwork

Code-drawn artwork requested by the maintainer on 2026-11-03. White bubbles mark
completed items; dark bubbles mark planned older-version support along a winding
road on a dark background. Thin connectors, flat cards and a monochrome palette
keep the presentation minimal. Wording and status follow the maintainer's requested roadmap. This graphic
does not replace the scoped build, console or compatibility validation records.

- `prosperocraft-roadmap.png`: 1800 × 1470 sharing image, rendered at twice the
  output resolution and downsampled.
- `prosperocraft-roadmap.svg`: editable vector version with live text.
- Generator: `tools/draw_roadmap.py`, using Pillow and supplied TrueType fonts.
  The delivered PNG uses Arial regular/bold; font files are not redistributed.
  No image-generation model or third-party illustration is used.

Regenerate from the repository root:

```sh
python3 tools/draw_roadmap.py --font /path/to/Arial.ttf --bold-font /path/to/Arial-Bold.ttf --output assets/roadmap
```

The first planned row follows the road from right to left, then the final row
continues left to right. Numbered planned milestones make the reading order
explicit. No release dates are assigned.
