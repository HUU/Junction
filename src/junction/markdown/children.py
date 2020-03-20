from typing import List, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import re
import xml.etree.ElementTree as etree


class ChildrenExtension(Extension):
    """Markdown extension for rendering the Confluence child pages macro.
    Example: `:include-children:`
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.parser.blockprocessors.register(
            ChildrenBlockProcessor(md.parser), "children", 25
        )


class ChildrenBlockProcessor(BlockProcessor):
    BLOCK_RE = re.compile(
        r"\s*:include-children:\s*", re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(self.BLOCK_RE.match(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        blocks.pop(0)
        etree.SubElement(
            parent,
            "ac:structured-macro",
            {
                "ac:name": "children",
                "ac:schema-version": "2",
                "ac:macro-id": "92c7a2c4-5cca-4ecf-81a2-946ef7388c71",
            },
        ).tail = "\n"


def makeExtension(**kwargs: Any) -> ChildrenExtension:
    return ChildrenExtension(**kwargs)
