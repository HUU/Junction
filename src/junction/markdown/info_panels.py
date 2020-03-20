from typing import List, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import re
import xml.etree.ElementTree as etree


class InfoPanelExtension(Extension):
    """Markdown extension for rendering the Confluence info panel macro.  Only supports
    the "original" info panels AKA info (blue), success (green), warning (yellow), and error (red).
    Example:
    ```
    Normal, introductory paragraph.

    Warning: info panels like this must be isolated into their own blocks with surrounding blank lines.

    This will be a plain old paragraph, and not included in the warning above.
    ```
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.parser.blockprocessors.register(
            InfoPanelBlockProcessor(
                "Info:", "info", "42afc5c4-fb53-4483-9f1a-a87a7ad033e6", md.parser
            ),
            "info-panel",
            25,
        )
        md.parser.blockprocessors.register(
            InfoPanelBlockProcessor(
                "Success:", "tip", "d60a142d-bc62-4f37-a091-7254c4472bdf", md.parser
            ),
            "success-panel",
            25,
        )
        md.parser.blockprocessors.register(
            InfoPanelBlockProcessor(
                "Warning:", "note", "9e14a573-943e-4691-919b-a9f6a389da71", md.parser
            ),
            "warning-panel",
            25,
        )
        md.parser.blockprocessors.register(
            InfoPanelBlockProcessor(
                "Error:", "warning", "2e759c9c-11f1-4959-82e7-901a2dc737d7", md.parser
            ),
            "error-panel",
            25,
        )


class InfoPanelBlockProcessor(BlockProcessor):
    def __init__(
        self, prefix: str, name: str, macro_id: str, *args: Any, **kwargs: Any
    ):
        self._prefix = prefix
        self._block_re = re.compile(
            r"\s*{}.*".format(prefix), re.MULTILINE | re.DOTALL | re.VERBOSE
        )
        self._name = name
        self._macro_id = macro_id
        super().__init__(*args, **kwargs)

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(self._block_re.match(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        raw_content = blocks.pop(0).lstrip(self._prefix).lstrip()
        info_panel = etree.SubElement(
            parent,
            "ac:structured-macro",
            {
                "ac:name": self._name,
                "ac:schema-version": "1",
                "ac:macro-id": self._macro_id,
            },
        )
        rich_text_body = etree.SubElement(info_panel, "ac:rich-text-body")

        self.parser.parseChunk(rich_text_body, raw_content)
        info_panel.tail = "\n"


def makeExtension(**kwargs: Any) -> InfoPanelExtension:
    return InfoPanelExtension(**kwargs)
