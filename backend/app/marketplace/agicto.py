"""Scrape model list and docs from https://agicto.com/model."""

from __future__ import annotations

import json
import re
from datetime import datetime

import httpx

AGICTO_LIST_URL = "https://agicto.com/model"
AGICTO_DETAIL_URL = "https://agicto.com/model/{slug}"
USER_AGENT = "Mozilla/5.0 (compatible; AIKnow/1.0; +https://github.com/aiknow)"
HTTP_TIMEOUT = httpx.Timeout(25.0, connect=10.0)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT})
    return _client


async def close_agicto_client() -> None:
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


def has_doc_content(content_md: str | None) -> bool:
    return bool(content_md and len(content_md) > 80)


def apply_fetched_detail(row, meta: dict | None, md: str) -> bool:
    if meta:
        row.input_price = meta.get("input_price", row.input_price)
        row.output_price = meta.get("output_price", row.output_price)
        row.scene = meta.get("scene") or row.scene
        row.provider = meta.get("provider") or row.provider
    if has_doc_content(md):
        row.content_md = md
        row.doc_fetched_at = datetime.utcnow()
        return True
    return False


_LIST_PATTERN = re.compile(
    r'\{"apiModelName":"([^"]+)","attrList":\[[^\]]*\],"category":\[[^\]]*\],'
    r'"companyId":(\d+),"companyName":"([^"]*)","contextLen":(\d+),"desc":"([^"]*)",'
    r'"discount":"[^"]*","icon":"[^"]*","iconText":"([^"]*)","inputPrice":([\d.]+),'
    r'"isFree":(\d+),"modelId":(\d+),"modelName":"([^"]+)","modelType":"[^"]*",'
    r'"normal":\d+,"outputPrice":([\d.]+),"price_off":\d+,"showPrice":[^,]+,'
    r'"tagList":\[[^\]]*\],"typeId":"([^"]*)","typeName":"([^"]*)","uniqueId":"([^"]+)"\}'
)


def _decode_chunk(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
    if not chunks:
        return html
    return json.loads('"' + chunks[-1] + '"')


def parse_agicto_list(html: str) -> list[dict]:
    blob = _decode_chunk(html)
    rows: list[dict] = []
    seen: set[str] = set()
    for m in _LIST_PATTERN.finditer(blob):
        g = m.groups()
        slug = g[13]
        if slug in seen:
            continue
        seen.add(slug)
        rows.append(
            {
                "slug": slug,
                "name": g[9],
                "provider": g[5] or g[2],
                "company_name": g[2],
                "scene": g[12],
                "type_id": g[11],
                "context_len": int(g[3]),
                "input_price": float(g[6]),
                "output_price": float(g[10]),
                "is_free": int(g[7]) == 1,
                "agicto_model_id": int(g[8]),
                "summary": g[4] or None,
                "source_url": AGICTO_DETAIL_URL.format(slug=slug),
            }
        )
    return rows


def _extract_md(html: str, ref: str) -> str:
    idx = html.find(f"{ref}:T")
    if idx < 0:
        return ""
    m = re.match(rf"{ref}:T[a-z0-9]+,(.*)", html[idx:], re.S)
    if not m:
        return ""
    rest = m.group(1)
    markers = ['\\",\\"icon\\"', '\\",\\"iconText\\"', '\\",\\"apiModelName\\"', '\\",\\"contextLen\\"']
    ends = [rest.find(marker) for marker in markers if rest.find(marker) >= 0]
    end = min(ends) if ends else min(len(rest), 8000)
    raw = rest[:end]
    return raw.replace("\\n", "\n").replace('\\"', '"').strip()


def parse_agicto_detail(html: str) -> tuple[dict | None, str]:
    refs = re.findall(r'mdContent\\":\\"\$(\d+)', html)
    if not refs:
        refs = re.findall(r'"mdContent":"\$(\d+)"', html)
    md = _extract_md(html, refs[0]) if refs else ""
    meta_m = re.search(
        r'iconText\\":\\"([^\\]*)\\".*?inputPrice\\":([\d.]+).*?modelName\\":\\"([^\\]+)\\".*?'
        r'outputPrice\\":([\d.]+).*?typeName\\":\\"([^\\]*)\\".*?uniqueId\\":\\"([^\\]+)\\"',
        html,
        re.S,
    )
    if not meta_m:
        meta_m = re.search(
            r'"iconText":"([^"]*)".*?"inputPrice":([\d.]+).*?"modelName":"([^"]+)".*?'
            r'"outputPrice":([\d.]+).*?"typeName":"([^"]*)".*?"uniqueId":"([^"]+)"',
            html,
            re.S,
        )
    if not meta_m:
        return None, md
    return {
        "provider": meta_m.group(1),
        "input_price": float(meta_m.group(2)),
        "name": meta_m.group(3),
        "output_price": float(meta_m.group(4)),
        "scene": meta_m.group(5),
        "slug": meta_m.group(6),
    }, md


async def fetch_agicto_list() -> list[dict]:
    client = _get_client()
    resp = await client.get(AGICTO_LIST_URL, timeout=httpx.Timeout(90.0, connect=10.0))
    resp.raise_for_status()
    return parse_agicto_list(resp.text)


async def fetch_agicto_detail(slug: str) -> tuple[dict | None, str]:
    client = _get_client()
    resp = await client.get(AGICTO_DETAIL_URL.format(slug=slug))
    resp.raise_for_status()
    return parse_agicto_detail(resp.text)


def entry_to_dict(row) -> dict:
    return {
        "id": row.id,
        "slug": row.slug,
        "name": row.name,
        "provider": row.provider,
        "company_name": row.company_name,
        "scene": row.scene,
        "context_len": row.context_len,
        "input_price": row.input_price,
        "output_price": row.output_price,
        "is_free": row.is_free,
        "summary": row.summary,
        "has_doc": has_doc_content(row.content_md),
        "source_url": row.source_url,
        "doc_fetched_at": row.doc_fetched_at.isoformat() if row.doc_fetched_at else None,
        "synced_at": row.synced_at.isoformat(),
    }


def entry_doc_dict(row) -> dict:
    return {
        "slug": row.slug,
        "has_doc": has_doc_content(row.content_md),
        "content_md": row.content_md if has_doc_content(row.content_md) else None,
        "doc_fetched_at": row.doc_fetched_at.isoformat() if row.doc_fetched_at else None,
    }


def entry_detail_dict(row) -> dict:
    data = entry_to_dict(row)
    data["content_md"] = row.content_md
    return data
