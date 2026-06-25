import requests
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

# Carry over Google's own styles so colours, fonts, and tables look correct
google_styles = '\n'.join(str(s) for s in soup.select('head style'))

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
  {google_styles}
  <style>
    /* Mobile responsiveness only — colours, fonts, and sizes come from Google Docs */
    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    * {{ max-width: 100% !important; }}
    div, p, span, section {{ width: auto !important; }}
    img {{ display: block; width: 100% !important; height: auto !important; }}

    /* Google Docs sets page margins as fixed pt values that don't scale on mobile.
       On small screens, strip all left/right margins and use body padding instead. */
    @media (max-width: 768px) {{
      * {{ margin-left: 0 !important; margin-right: 0 !important; }}
      body {{ padding: 0 16px !important; }}
    }}
  </style>
</head>
<body>
{content_html}
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully.")
