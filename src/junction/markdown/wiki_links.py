from typing import Tuple, Optional, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import LinkInlineProcessor
import xml.etree.ElementTree as etree
import html
import re


class WikiLinkExtension(Extension):
    """Markdown extension for rendering links prefixed with '&' as links to other pages
    in Confluence.  Links in Confluence are based on page titles e.g. `&[Display Text](Target Page Name)`
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.add("wiki-link", WikiLinkPattern(md), "<reference")


class WikiLinkPattern(LinkInlineProcessor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(r"\&\[", *args, **kwargs)

    def handleMatch(
        self, m: re.Match, data: str
    ) -> Tuple[Optional[etree.Element], Optional[int], Optional[int]]:
        text, index, handled = self.getText(data, m.end(0))

        if not handled:
            return None, None, None

        href, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        link = etree.Element("ac:link", {"ac:card-appearance": "inline"})
        etree.SubElement(
            link,
            "ri:page",
            {
                "ri:content-title": html.escape(href, quote=False),
                "ri:version-at-save": "1",
            },
        )
        etree.SubElement(link, "ac:link-body").text = text

        return link, m.start(0), index


def makeExtension(**kwargs: Any) -> WikiLinkExtension:
    return WikiLinkExtension(**kwargs)
