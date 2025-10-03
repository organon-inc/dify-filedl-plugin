# Voucher Files Export (Dify Tool Plugin)

LLM/コードノードの出力から、そのままダウンロードカード（`files` 変数）を返す最小ツール。

## Install

1. Build `.difypkg` or zip this folder and upload via Dify "Plugins".
2. Ensure plugin runner = Python, requirements install `dify-plugin` (>=0.5).
3. Enable permissions: Tools / Apps / Storage.  
   (Per Dify docs) 

## How to Use (Workflow)

### A) そのまま受け渡し（passthrough）
- 前のコードノードが `files` 相当の配列 JSON（`[{name,mime_type,b64_content}]`）を出す場合、
  ツールパラメタ:
  - `mode=passthrough`
  - `files_json` にその配列文字列を渡す  
→ ダウンロードカードが出ます。

### B) 生成（compose）
- `csv_text`（任意）、`result`、`audit`（JSON文字列またはプレーンテキスト）を渡す。
- `make_json_files=true` で `result.json` / `audit.json` も出力。
- CSV は `csv_filename` でファイル名指定。

## Variables
- BLOB を返すと `files` が自動で埋まり、UI にダウンロードカードが表示されます。
- `create_text_message` / `create_json_message` で `text` / `json` 変数にも echo します。
