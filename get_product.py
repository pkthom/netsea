#!/usr/bin/env python3
# get_product.py
# 使い方:
#   export NETSEA_TOKEN='YOUR_REAL_TOKEN'
#   python get_product.py 22556736-1            # items_22556736-1.json へ保存
#   python get_product.py 22556736-1 -          # 標準出力（ファイル保存しない）

import os, sys, json, urllib.request, urllib.error

API = "https://api.netsea.jp/buyer/v1/items"
TOKEN = os.environ.get("NETSEA_TOKEN")

def usage():
    print("Usage: NETSEA_TOKEN=... python get_product.py <direct_item_ids> [out.json|-]")
    sys.exit(1)

def post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "netsea-sample/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)

def rows_from(payload):
    if isinstance(payload, dict):
        return payload.get("data") or payload.get("items") or []
    if isinstance(payload, list):
        return payload
    return []

def fetch_single(id_str: str):
    # 1) まずはご要望通り direct_item_ids を「文字列」で投げる
    j = post_json(API, {"per_page": 1, "direct_item_ids": id_str}, TOKEN)
    rows = rows_from(j)
    if rows: return rows[0]

    # 2) 念のため direct_item_id（単数）でも試行
    j = post_json(API, {"per_page": 1, "direct_item_id": id_str}, TOKEN)
    rows = rows_from(j)
    if rows: return rows[0]

    # 3) もし数字のみ & EAN桁なら JAN 検索も試す
    if id_str.isdigit() and len(id_str) in (8, 12, 13, 14):
        j = post_json(API, {"per_page": 1, "jan_code": id_str}, TOKEN)
        rows = rows_from(j)
        if rows: return rows[0]

    return None

def main():
    if not TOKEN:
        sys.exit("NETSEA_TOKEN 未設定です。例: export NETSEA_TOKEN='YOUR_TOKEN'")
    if len(sys.argv) < 2:
        usage()

    did = sys.argv[1].strip()  # 第1引数: direct_item_ids（単一・文字列）
    out_path = sys.argv[2] if len(sys.argv) >= 3 else f"items_{did}.json"

    try:
        item = fetch_single(did)
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "ignore")
        except Exception:
            pass
        if e.code == 401:
            sys.exit("HTTP 401: 認証エラー（トークン無効の可能性）\n" + detail)
        if e.code == 403:
            sys.exit("HTTP 403: アクセス権なし（直送可・承認済み範囲外の可能性）\n" + detail)
        sys.exit(f"HTTP {e.code} {e.reason}\n{detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")

    if not item:
        sys.exit(f"not returned via API: '{did}'（API対象外 or ID不一致）")

    text = json.dumps(item, ensure_ascii=False, indent=2)  # ← 日本語そのまま
    if out_path == "-" or out_path == "":
        print(text)
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()

