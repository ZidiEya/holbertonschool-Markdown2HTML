#!/usr/bin/python3
"""
Convert a Markdown file to HTML.
Usage: ./markdown2html.py README.md README.html
"""

import sys
import os
import re
import hashlib

def md_to_html(md_file, html_file):
    """Convert Markdown content to HTML and save it to html_file."""
    with open(md_file, 'r') as f:
        lines = f.read().splitlines()

    html_lines = []
    in_ul = False
    in_ol = False
    paragraph_lines = []

    def flush_paragraph():
        """Flush collected paragraph lines into HTML."""
        nonlocal paragraph_lines
        if paragraph_lines:
            html_lines.append("<p>")
            for i, pline in enumerate(paragraph_lines):
                # Replace bold **text**
                pline = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', pline)
                # Replace emphasis __text__
                pline = re.sub(r'__(.*?)__', r'<em>\1</em>', pline)
                # Replace [[text]] with MD5
                pline = re.sub(r'\[\[(.*?)\]\]',
                               lambda m: hashlib.md5(m.group(1).encode()).hexdigest(),
                               pline)
                # Replace ((text)) by removing all c/C
                pline = re.sub(r'\(\((.*?)\)\)',
                               lambda m: re.sub(r'c', '', m.group(1), flags=re.IGNORECASE),
                               pline)
                if i > 0:
                    html_lines.append("<br/>")
                html_lines.append(pline)
            html_lines.append("</p>")
            paragraph_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if heading_match:
            flush_paragraph()
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            html_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        # Unordered list
        ul_match = re.match(r'^-\s+(.*)', stripped)
        if ul_match:
            flush_paragraph()
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{ul_match.group(1)}</li>")
            continue

        # Ordered list
        ol_match = re.match(r'^\*\s+(.*)', stripped)
        if ol_match:
            flush_paragraph()
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{ol_match.group(1)}</li>")
            continue

        # Paragraph
        paragraph_lines.append(stripped)

    # Flush remaining content
    flush_paragraph()
    if in_ul:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")

    # Write to output file
    with open(html_file, 'w') as f:
        for l in html_lines:
            f.write(l + "\n")

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} README.md README.html", file=sys.stderr)
        sys.exit(1)

    md_file = sys.argv[1]
    html_file = sys.argv[2]

    if not os.path.exists(md_file):
        print(f"Missing {md_file}", file=sys.stderr)
        sys.exit(1)

    md_to_html(md_file, html_file)
    sys.exit(0)

if __name__ == "__main__":
    main()
