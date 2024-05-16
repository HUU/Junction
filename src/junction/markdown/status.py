from typing import Tuple, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re


class StatusExtension(Extension):
    """Markdown extension that generates Confluence status macros (the little colored pills).
    Supports red, yellow, green, grey, blue, and purple.  Some examples:
    ```
    Milestone 1 &status-green:Complete;
    Milestone 2 &status-yellow:In Progress;
    Milestone 3 &status-grey:Planning;
    ```
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(StatusPattern("red"), "status-red", 25)
        md.inlinePatterns.register(StatusPattern("yellow"), "status-yellow", 25)
        md.inlinePatterns.register(StatusPattern("green"), "status-green", 25)
        md.inlinePatterns.register(StatusPattern("grey"), "status-grey", 25)
        md.inlinePatterns.register(StatusPattern("purple"), "status-purple", 25)
        md.inlinePatterns.register(StatusPattern("blue"), "status-blue", 25)


class StatusPattern(InlineProcessor):
    def __init__(self, color: str):
        self._color = color
        super().__init__(r"&status-{}:(?P<title>[^;]+);".format(self._color))

    def handleMatch(  # type: ignore
        self, match: re.Match[str], data: str
    ) -> Tuple[etree.Element, int, int]:
        el = etree.Element(
            "ac:structured-macro",
            {
                "ac:name": "status",
                "ac:schema-version": "1",
                "ac:macro-id": "d4fcf299-d2f0-4eec-807a-1e4a3c8fe0dc",
            },
        )

        etree.SubElement(el, "ac:parameter", {"ac:name": "title"}).text = match.group(
            "title"
        )
        etree.SubElement(el, "ac:parameter", {"ac:name": "colour"}).text = (
            self._color.capitalize()
        )

        return el, match.start(0), match.end(0)


def makeExtension(**kwargs: Any) -> StatusExtension:
    return StatusExtension(**kwargs)
