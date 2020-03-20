from typing import List, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import re
import xml.etree.ElementTree as etree


class TableOfContentsExtension(Extension):
    """Markdown extension for rendering the Confluence Table of Contents macro.
    Example: `:include-toc:`
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.parser.blockprocessors.register(
            TableOfContentsBlockProcessor(md.parser), "toc", 25
        )


class TableOfContentsBlockProcessor(BlockProcessor):
    TOC_BLOCK_RE = re.compile(
        r"\s*:include-toc:\s*", re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(self.TOC_BLOCK_RE.match(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        blocks.pop(0)
        etree.SubElement(
            parent,
            "ac:structured-macro",
            {
                "ac:name": "toc",
                "ac:schema-version": "1",
                "data-layout": "default",
                "ac:macro-id": "d4d3f545-d250-47ec-8f27-25fecf5eac5a",
            },
        ).tail = "\n"


def makeExtension(**kwargs: Any) -> TableOfContentsExtension:
    return TableOfContentsExtension(**kwargs)
