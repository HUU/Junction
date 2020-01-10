from markdown import Markdown
from markdown.extensions.sane_lists import SaneListExtension
from mdx_superscript import SuperscriptExtension
from mdx_subscript import SubscriptExtension
from mdx_emdash import EmDashExtension
from mdx_urlize import UrlizeExtension


junctionMarkdown = Markdown(
    extensions=[
        SaneListExtension(),
        SuperscriptExtension(),
        SubscriptExtension(),
        EmDashExtension(),
        UrlizeExtension()
    ]
)

def markdown_to_storage(text):
    result = junctionMarkdown.convert(text)
    junctionMarkdown.reset();
    return result