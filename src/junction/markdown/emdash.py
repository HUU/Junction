from typing import Any

import re
from markdown import Extension
from markdown.inlinepatterns import Pattern
from markdown import util, Markdown


class EmDashPattern(Pattern):
    """
    Replaces '---' with '&emdash;'.
    """

    def __init__(self) -> None:
        super(EmDashPattern, self).__init__("---")

    def handleMatch(self, m: re.Match[str]) -> str:
        # have to use special AMP_SUBSTITUTE character or it gets escaped
        return "{}mdash;".format(util.AMP_SUBSTITUTE)


class EmDashExtension(Extension):
    """
    Extension that replaces '---' with '&emdash;'.
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(EmDashPattern(), "emdashpattern", 100)


def makeExtension(**kwargs: Any) -> EmDashExtension:
    return EmDashExtension(**kwargs)
