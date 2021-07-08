import re
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class ChecklistExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        postprocessor = ChecklistPostprocessor(md)
        md.postprocessors.add("checklist", postprocessor, ">raw_html")


class ChecklistPostprocessor(Postprocessor):
    """Markdown extension that supports GitHub styled checklists for tasks, based on https://github.com/FND/markdown-checklist

    For example:
    - [ ] An incomplete task
    - [x] A completed task
    """

    item_with_children_pattern = re.compile(
        r"<li>\[([ Xx])\]((?!</li>).*)<ul>", re.MULTILINE
    )
    item_paragraph_pattern = re.compile(r"<p>\[([ Xx])\](.*)</p>", re.MULTILINE)
    item_pattern = re.compile(r"<li>\[([ Xx])\](.*)</li>", re.MULTILINE)

    def run(self, html: str) -> str:
        # Converts nested lists that start with a task
        html = re.sub(
            self.item_with_children_pattern, self._convert_item_with_children, html
        )
        # Converts paragraphs with the task syntax, in case the HTML parser created an extra line
        html = re.sub(self.item_paragraph_pattern, self._convert_item, html)
        # Converts regular list items
        html = re.sub(self.item_pattern, self._convert_item, html)
        return html

    def _convert_item(self, match: re.Match) -> str:
        """
        Converts an item without children, uses the offset of the match from the start of the HTML
        as the task ID
        """
        state, caption = match.groups()
        return render_item(caption, state != " ", match.start())

    def _convert_item_with_children(self, match: re.Match) -> str:
        """
        Converts an item with children, uses the offset of the match from the start of the HTML
        as the task ID
        """
        state, caption = match.groups()
        return render_item(caption, state != " ", match.start()) + "<ul><li>"


def render_item(caption: str, checked: bool, task_id: int) -> str:
    status = "complete" if checked else "incomplete"
    return f"""<ac:task-list>
<ac:task>
<ac:task-id>{task_id}</ac:task-id>
<ac:task-status>{status}</ac:task-status>
<ac:task-body>{caption}</ac:task-body>
</ac:task>
</ac:task-list>"""


def makeExtension(**kwargs: Any) -> ChecklistExtension:
    return ChecklistExtension(**kwargs)
