#!/usr/bin/env python3
"""Package a Markdown report as standalone HTML and/or PDF."""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Markdown accessibility report to HTML/PDF.")
    parser.add_argument("input", type=Path, help="source Markdown report")
    parser.add_argument("--html", type=Path, help="standalone HTML output")
    parser.add_argument("--pdf", type=Path, help="PDF output; requires WeasyPrint")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.html and not args.pdf:
        print("ERROR: specify --html and/or --pdf", file=sys.stderr)
        return 2
    try:
        source = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        import markdown
    except ImportError:
        print("ERROR: install development dependencies first: python -m pip install -r requirements-dev.txt", file=sys.stderr)
        return 1

    body = markdown.markdown(source, extensions=["tables", "fenced_code", "sane_lists", "toc"])
    title = next((line[2:].strip() for line in source.splitlines() if line.startswith("# ")), "Accessibility Audit Report")
    document = f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
@page {{ size: A4; margin: 18mm 16mm 20mm; }}
:root {{ color-scheme: light; }}
body {{ margin: 0; color: #152B3A; background: #F5F1E8; font-family: \"Noto Sans TC\", \"Noto Sans CJK TC\", sans-serif; font-size: 14px; line-height: 1.75; }}
main {{ max-width: 980px; margin: 0 auto; padding: 42px 48px; background: #FBF9F4; }}
h1 {{ margin: 0 0 22px; padding-bottom: 16px; border-bottom: 4px solid #E86A4A; font-family: \"Noto Sans TC\", sans-serif; font-size: 30px; line-height: 1.25; letter-spacing: -.04em; }}
h2 {{ margin: 34px 0 12px; padding-left: 11px; border-left: 3px solid #E86A4A; font-size: 20px; line-height: 1.35; }}
h3 {{ margin: 24px 0 10px; font-size: 16px; }}
p {{ margin: 9px 0; }}
blockquote {{ margin: 20px 0; padding: 12px 16px; border-left: 3px solid #5CB8A5; background: #E6F1ED; color: #35505A; }}
table {{ width: 100%; margin: 16px 0 22px; border-collapse: collapse; font-size: 12px; page-break-inside: auto; }}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; page-break-after: auto; }}
th {{ background: #152B3A; color: #FBF9F4; font-weight: 700; text-align: left; }}
th, td {{ padding: 8px 9px; border: 1px solid #D9D4C9; vertical-align: top; }}
tr:nth-child(even) td {{ background: #F2EFE7; }}
code {{ padding: 2px 5px; border-radius: 4px; background: #E8EFEC; color: #35505A; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .9em; }}
pre {{ overflow: auto; padding: 14px; border-radius: 8px; background: #152B3A; color: #F5F1E8; }}
a {{ color: #C45740; }}
@media print {{ body {{ background: white; }} main {{ max-width: none; padding: 0; background: white; }} a {{ color: inherit; text-decoration: none; }} }}
</style>
</head>
<body><main>{body}</main></body>
</html>
"""

    if args.html:
        output = args.html
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document, encoding="utf-8")
        print(f"WROTE {output}")

    if args.pdf:
        try:
            from weasyprint import HTML
        except ImportError:
            print("ERROR: PDF output requires WeasyPrint; install requirements-dev.txt", file=sys.stderr)
            return 1
        output = args.pdf
        output.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=document, base_url=str(args.input.parent)).write_pdf(str(output))
        print(f"WROTE {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
