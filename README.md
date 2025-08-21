# netsea

```
curl -s -H "Authorization: Bearer $NETSEA_TOKEN" \
  -H "Accept: application/json" \
  "https://api.netsea.jp/buyer/v1/categories?page=1&per_page=100" \
| python3 -c 'import sys,json;print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))' > categories.txt

curl -X POST "https://api.netsea.jp/buyer/v1/items" \
  -H "Authorization: Bearer $NETSEA_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"per_page":1,"direct_item_ids":"22556736-1"}'
```
