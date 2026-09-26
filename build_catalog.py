"""Inject the latest nornslist catalog.json snapshot into norns-catalog.html.

Usage:  python build_catalog.py [path-to-catalog.json]
Without an argument, downloads the current feed from GitHub.
"""
import io
import json
import re
import sys
import urllib.request

FEED = "https://raw.githubusercontent.com/seajaysec/nornslist/main/catalog.json"
HTML = "norns-catalog.html"
KEEP = ("Name", "Author", "Description", "Project URL", "Last Updated", "Tags",
        "Demo", "Documentation URL", "Community URL", "status", "stars",
        "engine", "score", "caps")

if len(sys.argv) > 1:
    with io.open(sys.argv[1], encoding="utf-8") as f:
        catalog = json.load(f)
else:
    with urllib.request.urlopen(FEED) as r:
        catalog = json.loads(r.read().decode("utf-8"))

slim = {
    "date": catalog.get("date", ""),
    "scripts": [{k: v for k, v in s.items() if k in KEEP} for s in catalog["scripts"]],
}
payload = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
# must not break out of the <script> block or the JS string literal context
payload = payload.replace("</", "<\\/").replace(" ", "\\u2028").replace(" ", "\\u2029")

with io.open(HTML, encoding="utf-8") as f:
    html = f.read()

block = '<script id="snapshot" type="application/json">%s</script>' % payload
html, n = re.subn(
    r"<!--SNAPSHOT:BEGIN-->.*?<!--SNAPSHOT:END-->",
    "<!--SNAPSHOT:BEGIN-->\n" + block + "\n<!--SNAPSHOT:END-->",
    html,
    flags=re.S,
)
if n != 1:
    sys.exit("snapshot markers not found in " + HTML)

with io.open(HTML, "w", encoding="utf-8", newline="") as f:
    f.write(html)

print("injected %d scripts (%s) into %s — %.0f KB total"
      % (len(slim["scripts"]), slim["date"], HTML, len(html.encode("utf-8")) / 1024))
