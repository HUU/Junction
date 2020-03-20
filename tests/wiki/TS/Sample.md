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