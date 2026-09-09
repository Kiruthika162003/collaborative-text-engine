"""HTML render: turn a document's Markdown into HTML, escaping the content it carries.

This renders the common Markdown a writing room uses into
HTML: headings, paragraphs, unordered and ordered lists,
blockquotes, fenced code, and the inline run of bold, italic,
inline code, and links. The order that keeps it safe is to
escape each line's text into HTML entities first, so a stray
angle bracket or ampersand in the prose becomes harmless, and
only then apply the inline Markdown, because the Markdown
markers survive escaping and the content does not, which is
the difference between a renderer and an injection. Fenced
code is escaped and emitted verbatim without inline
processing, since a star inside code is a star, not emphasis,
which is the whole reason code fences exist. The scope is the
common blocks, stated plainly: nested lists are flattened to
one level, tables and reference links are left to the modules
that own them, and inline nesting is shallow, code then link
then emphasis, so a bold link renders but a bold word inside
inline code does not, the trade a lightweight renderer makes
against being a full parser. What it will not do is emit
unescaped user text anywhere, because the one promise an HTML
renderer must never break is that the document's words cannot
become the document's markup, and every path here runs its
text through the escape first.
"""

from __future__ import annotations

import re

from loom.htmlescape import escape

FENCE = re.compile(r"^```")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
QUOTE = re.compile(r"^>\s?(.*)$")
UNORDERED = re.compile(r"^[-*+]\s+(.*)$")
ORDERED = re.compile(r"^\d+\.\s+(.*)$")

LINK = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")
CODE = re.compile(r"`([^`]+)`")
BOLD_STAR = re.compile(r"\*\*([^*]+)\*\*")
BOLD_UNDER = re.compile(r"__([^_]+)__")
ITALIC_STAR = re.compile(r"\*([^*]+)\*")
ITALIC_UNDER = re.compile(r"_([^_]+)_")


def _inline(text: str) -> str:
    text = escape(text)
    text = CODE.sub(r"<code>\1</code>", text)
    text = LINK.sub(r'<a href="\2">\1</a>', text)
    text = BOLD_STAR.sub(r"<strong>\1</strong>", text)
    text = BOLD_UNDER.sub(r"<strong>\1</strong>", text)
    text = ITALIC_STAR.sub(r"<em>\1</em>", text)
    return ITALIC_UNDER.sub(r"<em>\1</em>", text)


def _list_block(
    lines: list[str], start: int, pattern: re.Pattern, tag: str
) -> tuple[str, int]:
    items = []
    index = start
    while index < len(lines):
        match = pattern.match(lines[index])
        if match is None:
            break
        items.append(f"<li>{_inline(match.group(1))}</li>")
        index += 1
    body = "".join(items)
    return f"<{tag}>{body}</{tag}>", index


def render(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if FENCE.match(line):
            code = []
            index += 1
            while index < len(lines) and not FENCE.match(lines[index]):
                code.append(escape(lines[index]))
                index += 1
            index += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
            continue
        heading = HEADING.match(line)
        if heading is not None:
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            index += 1
            continue
        if UNORDERED.match(line):
            block, index = _list_block(lines, index, UNORDERED, "ul")
            out.append(block)
            continue
        if ORDERED.match(line):
            block, index = _list_block(lines, index, ORDERED, "ol")
            out.append(block)
            continue
        if QUOTE.match(line):
            quoted = []
            while index < len(lines) and QUOTE.match(lines[index]):
                quoted.append(QUOTE.match(lines[index]).group(1))
                index += 1
            out.append(f"<blockquote><p>{_inline(' '.join(quoted))}</p></blockquote>")
            continue
        if line.strip() == "":
            index += 1
            continue
        para = []
        while (
            index < len(lines)
            and lines[index].strip()
            and not HEADING.match(lines[index])
            and not FENCE.match(lines[index])
            and not UNORDERED.match(lines[index])
            and not ORDERED.match(lines[index])
            and not QUOTE.match(lines[index])
        ):
            para.append(lines[index])
            index += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(out)
