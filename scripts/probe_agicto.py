import json
import re
import httpx

r = httpx.get("https://agicto.com/model", follow_redirects=True, timeout=60)
print("status", r.status_code, "len", len(r.text))
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
if m:
    data = json.loads(m.group(1))
    print("next keys", list(data.keys()))
    props = data.get("props", {})
    print("pageProps keys", list(props.get("pageProps", {}).keys())[:20])
    pp = props.get("pageProps", {})
    for k, v in pp.items():
        if isinstance(v, list):
            print(k, "list", len(v), type(v[0]).__name__ if v else None)
        elif isinstance(v, dict):
            print(k, "dict", list(v.keys())[:10])
        else:
            print(k, type(v).__name__, str(v)[:80])
else:
    print("no __NEXT_DATA__")
    # try API patterns
    for pat in ["/api/model", "/api/models", "/api/v1/models"]:
        try:
            rr = httpx.get("https://agicto.com" + pat, timeout=10)
            print(pat, rr.status_code, rr.text[:200])
        except Exception as e:
            print(pat, e)
