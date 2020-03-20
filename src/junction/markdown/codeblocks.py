from typing import List, Any
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re


class CodeBlockExtension(Extension):
    """Markdown extension that supports GitHub styled fenced codeblocks with optional language specification.
    For example:
    ```c#
    public static class MyCSharp {
        public static void main(string[] args) {
            Console.WriteLine("Confluence will highlight this code using its built-in C# highlighter.");
        }
    }
    ```
    """

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.preprocessors.register(CodeBlockPreprocessor(md), "code_block", 25)


class CodeBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(
        r"""
(?P<fence>^(?:`{3,}))[ ]*         # Opening ```
(?P<lang>[\w#.+-]*)?[ ]*\n        # Optional lang
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$""",
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )
    CODE_WRAP = """
<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="f3c5f016-dac0-4a3d-b154-7ccd862ab463">%s
  <ac:plain-text-body>
    <![CDATA[%s]]>
  </ac:plain-text-body>
</ac:structured-macro>"""
    LANG_TAG = '\n  <ac:parameter ac:name="language">%s</ac:parameter>'

    def run(self, lines: List[str]) -> List[str]:
        text = "\n".join(lines)
        while match := self.FENCED_BLOCK_RE.search(text):
            lang = ""
            if match.group("lang"):
                lang = self.LANG_TAG % match.group("lang")

            code = self.CODE_WRAP % (lang, match.group("code"))

            placeholder = self.md.htmlStash.store(code)
            text = "{}\n{}\n{}".format(
                text[: match.start()], placeholder, text[match.end() :]
            )

        return text.split("\n")


def makeExtension(**kwargs: Any) -> CodeBlockExtension:
    return CodeBlockExtension(**kwargs)
