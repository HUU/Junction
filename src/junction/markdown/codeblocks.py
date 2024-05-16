from typing import Any
from markdown import Markdown

CODE_WRAP = """<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="f3c5f016-dac0-4a3d-b154-7ccd862ab463">%s
  <ac:plain-text-body>
    <![CDATA[%s]]>
  </ac:plain-text-body>
</ac:structured-macro>"""
LANG_TAG = '\n  <ac:parameter ac:name="language">%s</ac:parameter>'


def confluence_code_format(
    source: str,
    language: str,
    class_name: str,
    options: dict,
    md: Markdown,
    **kwargs: Any
) -> str:
    return CODE_WRAP % (LANG_TAG % language if language else "", source)
