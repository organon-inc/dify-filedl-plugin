from __future__ import annotations

import base64
import json
from typing import Any, Generator, List, Optional

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 使い方：
# - mode=passthrough なら、files_json の配列（name, mime_type, b64_content）をそのまま BLOB 生成
# - mode=compose なら、csv_text/result/audit から BLOB を生成
# - さらに result/audit は text/json 変数にも流しておく（UI 側のデバッグにも便利）

class ExportFilesTool(Tool):
    def _parse_json_array(self, s: Optional[str]) -> List[dict]:
        if not s:
            return []
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return v
            return []
        except Exception:
            return []

    def _json_or_text(self, v: Optional[str]) -> Any:
        if v is None:
            return None
        try:
            return json.loads(v)
        except Exception:
            return v

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        mode: str = (tool_parameters.get("mode") or "compose").lower()

        # 1) Passthrough: 前ノードの files 構造をそのままダウンロードカード化
        if mode == "passthrough":
            files = self._parse_json_array(tool_parameters.get("files_json"))
            emitted = 0
            for f in files:
                name = f.get("name") or "file.bin"
                mime = f.get("mime_type") or "application/octet-stream"
                b64  = f.get("b64_content")
                if not b64:
                    continue
                try:
                    blob = base64.b64decode(b64)
                except Exception:
                    continue
                yield self.create_blob_message(
                    content=blob,
                    filename=name,
                    mime_type=mime,
                )
                emitted += 1

            if emitted == 0:
                # 何も作れなかった場合は説明文を返す
                yield self.create_text_message("No files emitted in passthrough mode.")
            return

        # 2) Compose: csv_text / result / audit からファイル生成
        csv_text: Optional[str] = tool_parameters.get("csv_text")
        csv_filename: str = tool_parameters.get("csv_filename") or "export.csv"
        result_raw: Optional[str] = tool_parameters.get("result")
        audit_raw: Optional[str] = tool_parameters.get("audit")
        make_json_files: bool = bool(tool_parameters.get("make_json_files", True))

        emitted = 0

        # CSV
        if csv_text:
            yield self.create_blob_message(
                content=csv_text.encode("utf-8-sig"),
                filename=csv_filename,
                mime_type="text/csv",
            )
            emitted += 1

        # result / audit を UI 変数にも置く（text/json）
        result_parsed = self._json_or_text(result_raw)
        audit_parsed  = self._json_or_text(audit_raw)

        if result_parsed is not None:
            if isinstance(result_parsed, (dict, list)):
                yield self.create_json_message(result_parsed)
            else:
                yield self.create_text_message(str(result_parsed))

        if audit_parsed is not None:
            if isinstance(audit_parsed, (dict, list)):
                yield self.create_json_message(audit_parsed)
            else:
                yield self.create_text_message(str(audit_parsed))

        # JSONファイル化
        if make_json_files:
            if result_parsed is not None:
                data = result_parsed if isinstance(result_parsed, (dict, list)) else {"value": str(result_parsed)}
                yield self.create_blob_message(
                    content=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                    filename="result.json",
                    mime_type="application/json",
                )
                emitted += 1
            if audit_parsed is not None:
                data = audit_parsed if isinstance(audit_parsed, (dict, list)) else {"value": str(audit_parsed)}
                yield self.create_blob_message(
                    content=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                    filename="audit.json",
                    mime_type="application/json",
                )
                emitted += 1

        if emitted == 0 and not (result_parsed or audit_parsed):
            yield self.create_text_message("No files emitted in compose mode.")
