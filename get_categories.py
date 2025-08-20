#!/usr/bin/env python3
import os, sys, json, time, urllib.request, urllib.parse, urllib.error
BASE = "https://api.netsea.jp/buyer/v1/categories"
TOKEN = os.environ.get("NETSEA_TOKEN")
PER_PAGE = 100
HEAD = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}

if not TOKEN:
    sys.exit("NETSEA_TOKEN 未設定です。例: export NETSEA_TOKEN='YOUR_TOKEN'")

def http_get(page):
    url = f"{BASE}?"+urllib.parse.urlencode({"page": page, "per_page": PER_PAGE})
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise urllib.error.HTTPError(url, resp.status, resp.reason, resp.headers, None)
        return json.load(resp)

def to_rows_meta(payload):
    if isinstance(payload, list):
        return payload, {}
    if isinstance(payload, dict):
        rows = payload.get("data") or payload.get("items") or []
        meta = payload.get("meta") or {}
        return rows, meta
    return [], {}

def save(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def main(out_path="categories_all.json", max_pages=1000):
    all_rows, seen, page = [], set(), 1
    while page <= max_pages:
        data = http_get(page)
        rows, meta = to_rows_meta(data)
        if not rows:
            print(f"page={page}: no rows; stop")
            break

        # 新規だけ追加
        new = [r for r in rows if str(r.get("id")) not in seen]
        for r in new:
            seen.add(str(r.get("id")))
        all_rows.extend(new)

        print(f"page={page}: fetched={len(rows)}, new={len(new)}, total_unique={len(all_rows)}")

        # 途中保存（空ファイルを避ける）
        save(out_path, all_rows)

        # 終了条件
        last_page = meta.get("last_page")
        if last_page and page >= int(last_page):
            print("hit last_page; stop")
            break
        if len(rows) < PER_PAGE:
            print("rows < per_page; stop")
            break
        if len(new) == 0:
            print("no new rows (same page repeating?); stop")
            break

        page += 1
        time.sleep(0.3)

    print(f"done: pages_seen={page}, unique_total={len(all_rows)}, saved={out_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "categories_all.json"
    main(out)

