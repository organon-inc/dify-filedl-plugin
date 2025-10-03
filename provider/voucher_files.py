from __future__ import annotations
from dify_plugin import ToolProvider

class Provider(ToolProvider):
    """
    認証がいらない最小実装。
    必要であれば credentials の検証や共有セッションの初期化をここで行う。
    """
    pass
