from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree


class StatusExtension(Extension):
    """ Markdown extension that generates Confluence status macros (the little colored pills).
    Supports red, yellow, green, grey, blue, and purple.  Some examples:
    ```
    Milestone 1 &status-green:Complete;
    Milestone 2 &status-yellow:In Progress;
    Milestone 3 &status-grey:Planning;
    ```
    """

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add("status-red", StatusPattern("red"), "<reference")
        md.inlinePatterns.add("status-yellow", StatusPattern("yellow"), "<reference")
        md.inlinePatterns.add("status-green", StatusPattern("green"), "<reference")
        md.inlinePatterns.add("status-grey", StatusPattern("grey"), "<reference")
        md.inlinePatterns.add("status-purple", StatusPattern("purple"), "<reference")
        md.inlinePatterns.add("status-blue", StatusPattern("blue"), "<reference")


class StatusPattern(InlineProcessor):
    def __init__(self, color):
        self._color = color
        super().__init__(r"&status-{}:(?P<title>[^;]+);".format(self._color))

    def handleMatch(self, match, data):
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
        etree.SubElement(
            el, "ac:parameter", {"ac:name": "colour"}
        ).text = self._color.capitalize()

        return el, match.start(0), match.end(0)


def makeExtension(*args, **kwargs):
    return StatusExtension(*args, **kwargs)
