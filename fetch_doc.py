import requests
import re
from bs4 import BeautifulSoup

PUB_URL = (
    'https://docs.google.com/document/d/e/'
    '2PACX-1vRTSAwtaZt2blbn-Qp0hTO8i8x0SvRe4TvaAA5qpyRQa0kSbs0vMC7EskBrXQwUWq9N734T0ZHuynPF'
    '/pub'
)

SYSTEM_FONTS = {
    'arial', 'helvetica', 'georgia', 'times', 'times new roman', 'verdana',
    'trebuchet ms', 'courier', 'courier new', 'sans-serif', 'serif',
    'monospace', 'sans', 'roboto', 'google sans', 'robotodraft'
}

headers = {'User-Agent': 'Mozilla/5.0 (compatible; site-builder/1.0)'}
response = requests.get(PUB_URL, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

for el in soup.select('#header, #footer, #banners'):
    el.decompose()

# Auto-detect and load Google Fonts
all_css = ' '.join(s.get_text() for s in soup.select('style'))
raw_fonts = re.findall(r'font-family:\s*["\']([^"\']+)["\']', all_css)
google_fonts = []
seen = set()
for name in raw_fonts:
    name = name.strip()
    if name.lower() not in SYSTEM_FONTS and name.lower() not in seen and len(name) > 2:
        seen.add(name.lower())
        google_fonts.append(name)

font_link = ''
if google_fonts:
    families = '&family='.join(
        f.replace(' ', '+') + ':ital,wght@0,400;0,700;1,400'
        for f in google_fonts
    )
    font_link = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'  <link href="https://fonts.googleapis.com/css2?family={families}&display=swap" rel="stylesheet">'
    )

# Extract the background colour from .doc-content's CSS classes so we can
# match it on <body> — no hardcoding. We look up each class on the element
# and find the first one that declares a background-color in the CSS.
bg_color = '#ffffff'  # safe fallback
doc_content_el = soup.select_one('.doc-content')
if doc_content_el:
    for cls in doc_content_el.get('class', []):
        match = re.search(
            rf'\.{re.escape(cls)}\s*\{{[^}}]*background-color:\s*(#[0-9a-fA-F]{{3,6}})',
            all_css
        )
        if match:
            bg_color = match.group(1)
            break

google_links  = '\n'.join(str(el) for el in soup.select('head link[rel="stylesheet"]'))
google_styles = '\n'.join(str(s)  for s  in soup.select('head style'))

content = soup.select_one('#contents') or soup.body
content_html = str(content) if content else '<p>Content not found.</p>'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Friends of Karen Donnelly Park</title>
  <meta name="description" content="Karen Donnelly Park is a small but special green space in the heart of Pennsport, South Philadelphia.">
  {font_link}
  {google_links}
  {google_styles}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    * {{ max-width: 100% !important; }}
    img {{ display: block; width: 100% !important; height: auto !important; }}

    /* Match body background to the doc's content background so nothing shows through */
    html, body {{
      margin: 0 !important;
      padding: 0 !important;
      background-color: {bg_color} !important;
    }}

    /* Remove the outer white wrapper padding so lavender fills edge-to-edge */
    #contents {{
      padding: 0 !important;
      margin: 0 !important;
    }}

    /* Cap width, centre, and halve the top padding (54pt → 27pt).
       Body background matches lavender so the sides fill on wide screens. */
    .doc-content {{
      max-width: 900px !important;
      margin: 0 auto !important;
      padding-top: 27pt !important;
    }}

    /* On mobile, the original ~85px side padding is too tight — reduce it */
    @media (max-width: 600px) {{
      .doc-content {{
        padding-left: 20px !important;
        padding-right: 20px !important;
      }}
    }}
  </style>
</head>
<body>
{content_html}
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"index.html updated. Fonts: {', '.join(google_fonts) or 'none detected'}. Background: {bg_color}")
