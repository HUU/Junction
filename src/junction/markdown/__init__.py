import logging

from markdown import Markdown
from markdown.extensions.sane_lists import SaneListExtension
from mdx_superscript import SuperscriptExtension
from mdx_subscript import SubscriptExtension
from mdx_emdash import EmDashExtension
from mdx_urlize import UrlizeExtension

from junction.markdown.codeblocks import CodeBlockExtension
from junction.markdown.status import StatusExtension
from junction.markdown.toc import TableOfContentsExtension
from junction.markdown.children import ChildrenExtension
from junction.markdown.info_panel import InfoPanelExtension
from junction.markdown.wiki_link import WikiLinkExtension


logger = logging.getLogger(__name__)


junctionMarkdown = Markdown(
    extensions=[
        SaneListExtension(),
        SuperscriptExtension(),
        SubscriptExtension(),
        EmDashExtension(),
        UrlizeExtension(),
        CodeBlockExtension(),
        StatusExtension(),
        TableOfContentsExtension(),
        ChildrenExtension(),
        InfoPanelExtension(),
        WikiLinkExtension(),
    ]
)


def markdown_to_storage(text) -> str:
    if hasattr(text, "decode"):
        text = text.decode("utf-8", "ignore")
    logger.debug("Compiling markdown to Confluence storage format: %s", text)
    result = junctionMarkdown.convert(text)
    junctionMarkdown.reset()
    logger.debug("Resulting Confluence storage format: %s", result)
    return result
