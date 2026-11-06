"""Generate high-quality executive PDF of DEMO_STORYBOARD.md using Google Cloud styling."""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_MD = PROJECT_ROOT / "DEMO_STORYBOARD.md"
DOCS_DIR = PROJECT_ROOT / "docs"
PDF_STORYBOARD = DOCS_DIR / "DEMO_STORYBOARD.pdf"
PDF_STORY_BOARD_ALIAS = DOCS_DIR / "Story_Board.pdf"

CSS = """
@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-right {
        content: "OFFICIAL-SENSITIVE // DEMO TRACK";
        font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
        font-size: 7.5pt;
        color: #5f6368;
    }
    @bottom-center {
        content: "Royal Air Force · Carrier Strike Group · F-35 Fleet Sustainment Agent Platform";
        font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
        font-size: 7.5pt;
        color: #5f6368;
    }
}
body {
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.55;
    color: #202124;
    max-width: 100%;
}
.header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #4285F4;
    padding-bottom: 8px;
    margin-bottom: 16px;
}
.classification {
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 1px;
    color: #5f6368;
}
h1 {
    font-size: 18pt;
    color: #1a73e8;
    margin-top: 0.8em;
    margin-bottom: 0.3em;
    font-weight: 700;
}
h2 {
    font-size: 13.5pt;
    color: #202124;
    border-bottom: 1.5px solid #dadce0;
    padding-bottom: 4px;
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}
h3 {
    font-size: 11pt;
    color: #3c4043;
    margin-top: 1.1em;
    margin-bottom: 0.4em;
    page-break-after: avoid;
}
p {
    margin: 0.5em 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.2em 0;
    font-size: 8.2pt;
    page-break-inside: auto;
}
tr {
    page-break-inside: avoid;
    page-break-after: auto;
}
tr:nth-child(even) {
    background-color: #f8f9fa;
}
th, td {
    border: 1px solid #dadce0;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #f1f3f4;
    color: #202124;
    font-weight: 600;
}
code {
    background-color: #f1f3f4;
    color: #d93025;
    padding: 0.15em 0.35em;
    border-radius: 3px;
    font-family: 'Roboto Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 88%;
}
pre {
    background-color: #f8f9fa;
    padding: 10px 14px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 8pt;
    border: 1px solid #dadce0;
    page-break-inside: avoid;
}
pre code {
    background-color: transparent;
    color: #202124;
    padding: 0;
}
blockquote {
    border-left: 4px solid #4285F4;
    margin: 1em 0;
    padding: 6px 12px;
    background-color: #f8fafd;
    color: #3c4043;
}
div.tip, div.note, div.important, div.warning, div.caution {
    padding: 8px 12px;
    margin: 1em 0;
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}
div.tip {
    border-left: 4px solid #34a853;
    background-color: #f6fbf7;
}
div.note {
    border-left: 4px solid #4285F4;
    background-color: #f8fafd;
}
div.important {
    border-left: 4px solid #ea4335;
    background-color: #fdf7f7;
}
div.warning {
    border-left: 4px solid #fbbc04;
    background-color: #fffdf5;
}
div.caution {
    border-left: 4px solid #ea4335;
    background-color: #fdf7f7;
}
div.title {
    font-weight: 700;
    margin-bottom: 4px;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
}
div.tip div.title { color: #1e8e3e; }
div.note div.title { color: #1a73e8; }
div.important div.title { color: #d93025; }
div.warning div.title { color: #b06000; }
div.caution div.title { color: #d93025; }
hr {
    border: 0;
    border-top: 1px solid #dadce0;
    margin: 1.5em 0;
}
ul, ol {
    margin: 0.4em 0;
    padding-left: 20px;
}
li {
    margin: 0.25em 0;
}
"""


def build_pdf():
    print(f"Reading markdown from: {STORYBOARD_MD}")
    assert STORYBOARD_MD.exists(), f"Source file {STORYBOARD_MD} not found"

    # Step 1: Convert GFM Markdown to HTML5 via pandoc
    proc = subprocess.run(
        ["pandoc", "--from=gfm", "--to=html5", str(STORYBOARD_MD)],
        capture_output=True,
        text=True,
        check=True,
    )
    body_html = proc.stdout

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Executive Demo Storyboard: F-35 Fleet Sustainment</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="header-bar">
    <span class="classification">OFFICIAL-SENSITIVE // DEMO TRACK</span>
    <span class="classification">ROYAL AIR FORCE · CSG · 617 SQN</span>
</div>
{body_html}
</body>
</html>"""

    html_path = DOCS_DIR / "DEMO_STORYBOARD.html"
    html_path.write_text(full_html, encoding="utf-8")
    print(f"HTML rendered to: {html_path}")

    # Step 2: Convert HTML to PDF via headless Google Chrome
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={PDF_STORYBOARD}",
        str(html_path),
    ]
    subprocess.run(cmd, check=True)
    print(f"PDF generated at: {PDF_STORYBOARD} ({PDF_STORYBOARD.stat().st_size} bytes)")

    # Also write Story_Board.pdf alias
    PDF_STORY_BOARD_ALIAS.write_bytes(PDF_STORYBOARD.read_bytes())
    print(f"Alias written to: {PDF_STORY_BOARD_ALIAS} ({PDF_STORY_BOARD_ALIAS.stat().st_size} bytes)")


if __name__ == "__main__":
    build_pdf()
