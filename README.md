![Junction, publish and manage Confluence with git workflows](https://github.com/HUU/Junction/raw/master/docs/logo.png?raw=true)

With Junction you can write and manage your documentation directly in your codebase, using Markdown and your existing Git workflows (pull requests, code review, release branches, etc) and then automatically publish your changes to Confluence.  This gives you the best of both worlds: in-repo documentation that fits natively into your development workflows, with the discoverability and centrality of Confluence.

![MIT License](https://img.shields.io/badge/license-MIT-green) [![Python 3.8](https://img.shields.io/badge/python-3.8-blue)](https://pypi.org/project/confluence-junction) ![Build and Test](https://github.com/HUU/Junction/workflows/Build%20and%20Test/badge.svg)

# Install

Ensure you are using Python 3.8 (or newer); Junction does not work with older versions of Python.  Install using `pip`:
```sh
pip install confluence-junction
```
This will install the library and CLI.
In your Python code:
```python
import junction
```
In your shell:
```sh
junction --help
```

# Overview

Junction works by inspecting the changes made on a commit-by-commit basis to your Git repository, and determining what needs to be changed in Confluence to reflect those changes.  Junction (currently) expects to manage the entire [space in Confluence](https://confluence.atlassian.com/doc/spaces-139459.html).  Thus when using Junction you must tell it which Space to target and update.  You must not manually change, create, or modify pages in the target space, or else Junction may be unable to synchronize the state in Git with the state in Confluence.

To allow mixing code (and other items) with markdown files for Junction in a single repository, you can tell Junction a subpath within your repository that functions as the root e.g. all markdown files will be kept in `docs/`.  All files should end with the `.md` extension.

The page will gets its title from the file name, and its contents will be translated into Confluence markup.  See [this example for what output looks like in Confluence](#output-example).

# Usage

Collect a set of credentials that Junction will use to login to Confluence.  You will need to create an [API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html) to use instead of a password.  **I recommend you make a dedicated user account with access permissions limited to the space(s) you want to manage with Junction**.

In your git repository, create a folder structure and markdown files you would like to publish.  Commit those changes.
```
.
├── (your code and other files)
└── docs/
    ├── Welcome.md
    ├── Installation.md
    └── Advanced Usage
    |   ├── Airflow.md
    |   ├── Visual Studio Online.md
    |   ├── Atlassian Bamboo.md
    |   └── GitHub Actions.md
    └── Credits.md
```

Junction is designed as a library, and also provides "helpers" that make using it in different contexts easy (in particularly, as part of automated workflows e.g. in post-push builds).

The simplest way to use Junction is the included CLI `junction`:
```sh
junction -s "SPACE_KEY" -c "https://jihugh.atlassian.net/wiki/rest/api" -u "account@email.com" -p "YOUR_API_ACCESS_TOKEN" delta --content-path docs/ HEAD~5 master
```
> You can put the API, user, and key into environment variables to avoid specifying them for every invocation of Junction.  The variables are `CONFLUENCE_API`, `CONFLUENCE_API_USER`, and `CONFLUENCE_API_KEY` respectively.

The CLI is fully documented, so make use of the `--help` option to navigate all of the configuration options.

### Dry Run

You can check what the `junction` CLI will do to your space without actually uploading the changes to Confluence by using the `--dry-run` flag.

![Dry run example output](https://github.com/HUU/Junction/raw/master/docs/dry_run_example.gif?raw=true)

### Python Library

Using the Python library will let you create your own wrappers and tools, for example an AirFlow DAG.  Here is an equivalent of the above CLI usage in Python:

```python
from pathlib import Path
from git import Repo
from junction.git import find_commits_on_branch_after, filter_modifications_to_folder, get_modifications
from junction.delta import Delta
from junction.confluence import Confluence

cf = Confluence("https://jihugh.atlassian.net/wiki/rest/api", "account@email.com", "YOUR_API_ACCESS_TOKEN", "SPACE_KEY")
repo = Repo("."). # current working directory must be the root of the Git repository for this to work

commits = find_commits_on_branch_after("master", "HEAD~5", repo)
deltas = [Delta.from_modifications(filter_modifications_to_folder(get_modification(commit), Path("docs/"))) for commit in commits]

for delta in deltas:
    delta.execute(cf)
```

# Output Example

The following markdown sample, stored in `Sample.md`, produces a page in Confluence that looks like [this](https://github.com/HUU/Junction/blob/master/docs/example_output.png?raw=true).  This shows all of the major supported features and markup.  It is intentionally very similar to GitHub-style markdown, with some extensions and differences to account for Confluence-specific features.

    # Text

    It's very easy to make some words **bold** and other words *italic* with Markdown. You can even [link to Google!](http://google.com).
    Even some fancy formats like Subscripts~with tilde~ and Superscripts^with caret^.

    # Lists

    Sometimes you want numbered lists:

    1. One
    2. Two
    3. Three

    Sometimes you want bullet points:

    * Start a line with a star
    * Profit!

    Alternatively,

    - Dashes work just as well
    - And if you have sub points, put four spaces before the dash or star:
        - Like this
        - And this

    # Headers

    Sometimes it's useful to have different levels of headings to structure your documents. Start lines with a `#` to create headings. Multiple `##` in a row denote smaller heading sizes.

    ### This is a third-tier heading

    You can use one `#` all the way up to `######` six for different heading sizes.

    # Blockquotes

    If you'd like to quote someone, use the > character before the line:

    > Coffee. The finest organic suspension ever devised... I beat the Borg with it.
    > - Captain Janeway

    # Code

    You can embed `inline code fragments` by surrounding it in backticks.  For longer blocks of
    code, use "code fencing":

    ```
    if (isAwesome){
      return true
    }
    ```

    And if you'd like to use syntax highlighting, include the language:

    ```php
    <?php
        echo "Hello World"
    ?>
    ```

    # Tables

    You can create tables by assembling a list of words and dividing them with hyphens `-` (for the first row), and then separating each column with a pipe `|`:

    First Header | Second Header
    ------------ | -------------
    Content from cell 1 | Content from cell 2
    Content in the first column | Content in the second column

    # Confluence-specific Elements

    You can link to other wiki pages by referencing their page titles.  Use normal link syntax, but prepend a `&` like &[this](Page Title).

    ## Supported Macros

    You can embed the Confluence child pages macro by placing it on its own line:

    :include-children:

    ...or the table of contents macro:

    :include-toc:

    ## Status Blocks

    You can create Confluence status macros (colored pills), including in the middle of the line &status-green:like this;

    &status-green:Complete; &status-yellow:In Progress; &status-grey:Planning; &status-red:Failed; &status-blue:Unknown; &status-purple:Cancelled;

    ## Info Panels

    Info: You can create info panels by prepending a paragraph with one of `Info:`, `Warning:`, `Error:`, or `Success:`.

    Warning: The prefix will be removed from the contents.

    Error: You cannot put multiple paragraphs inside an info panel, just a single block of text
    like this.

    Success: like other block elements, each info panel must be located on its own line (fenced between two new lines).

# Contributing

This is a hobby project of mine, and I may not be able to work on it immediately upon request.   If you are interested in contributing, feel free to open a PR by following [the contribution guidelines](https://github.com/HUU/Junction/blob/master/CONTRIBUTING.md).
