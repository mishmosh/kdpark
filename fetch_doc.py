import requests
import re
from bs4 import BeautifulSoup

PUB_URL = (
    'https://docs.google.com/document/d/e/'
    '2PACX-1vRTSAwtaZt2blbn-Qp0hTO8i8x0SvRe4TvaAA5qpyRQa0kSbs0vMC7EskBrXQwUWq9N734T0ZHuynPF'
    '/pub'
)

headers = {'User-Agent': 'Mozilla/5.0 (compatible; site-builder/1.0)'}
response = requests.get(PUB_URL, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

# Remove Google's "Published using Google Docs" header bars and footer
for el in soup.select('#header, #footer, #banners'):
    el.decompose()

# Fix mobile margins:
# Google Docs encodes page margins as fixed pt values in generated CSS classes
# (e.g. .c2 { margin-left: 72pt }). Find those exact classes and add a mobile
# override that zeroes them — desktop margins stay completely untouched.
for style_tag in soup.select('head style'):
    css = style_tag.string or ''
    mobile_overrides = []
    for match in re.finditer(
        r'(\.[a-zA-Z0-9_-]+)\s*\{([^}]*(?:margin-left|margin-right)[^}]*pt[^}]*)\}',
        css
    ):
        selector = match.group(1)
        mobile_overrides.append(
            f'{selector} {{ margin-left: 0 !important; margin-right: 0 !important; }}'
        )
    if mobile_overrides:
        mobile_block = (
            '\n@media (max-width: 600px) {\n'
            + '\n'.join(mobile_overrides)
            + '\nbody { padding: 0 16px !important; }\n}'
        )
        style_tag.string = css + mobile_block

# Carry over Google's font <link> tags AND <style> blocks so nothing is lost
google_links  = '\n'.join(str(el) for el in soup.select('head link[rel="stylesheet"]'))
google_styles = '\n'.join(str(s)  for s  in soup.select('head style'))

# Extract the document body content
content = soup.select_one('#contents') or soup.body
content_html = str(content) if content else '<p>Content not found.</p>'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Friends of Karen Donnelly Park</title>
  <meta name="description" content="Karen Donnelly Park is a small but special green space in the heart of Pennsport, South Philadelphia.">
  {google_links}
  {google_styles}
  <style>
    /* Responsive layout only — colours, fonts, and sizes come from Google Docs */
    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    * {{ max-width: 100% !important; }}
    img {{ display: block; width: 100% !important; height: auto !important; }}
  </style>
</head>
<body>
{content_html}
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully.")
