"""Template engine: variables, conditionals, and loops over a context, mustache-style.

Where the mail-merge module fills flat placeholders, this is
the small logic-bearing template a report or an email needs: a
double-brace variable, a hash-if block that renders its body
only when a value is truthy, and a hash-each block that renders
its body once per item of a list. It works in two stages, the
right shape for anything with nesting: tokenize the template
into text, variables, and block markers, parse those into a
tree where each block owns its body, and render the tree
against a context. Two stages rather than one because a block's
body must render with a different context, the each block once
per item, and a tree makes that a recursion where a single pass
would be a tangle of state. Inside an each block the current
item is the dot variable, and a dict item's keys are variables
too, with the outer context still visible so a loop can
reference a value from around it. A variable the context does
not hold renders empty rather than raising, because a template
filled with real data will have gaps and a missing optional
field is a blank, not a crash, though that does mean a
misspelled variable name fails silently as an empty string, the
trade every logic-less template makes and named here. Dotted
paths walk nested dicts, so a context of records addresses a
field inside one, and the whole thing holds no eval and runs no
caller code, which is the safety a template rendered from
untrusted data must keep: it substitutes and branches and
loops, and it does nothing else.
"""

from __future__ import annotations

import re

TAG = re.compile(r"\{\{(.*?)\}\}")


def _tokenize(template: str) -> list[tuple]:
    tokens: list[tuple] = []
    last = 0
    for match in TAG.finditer(template):
        if match.start() > last:
            tokens.append(("text", template[last : match.start()]))
        expr = match.group(1).strip()
        if expr.startswith("#if "):
            tokens.append(("if", expr[4:].strip()))
        elif expr == "/if":
            tokens.append(("endif",))
        elif expr.startswith("#each "):
            tokens.append(("each", expr[6:].strip()))
        elif expr == "/each":
            tokens.append(("endeach",))
        else:
            tokens.append(("var", expr))
        last = match.end()
    if last < len(template):
        tokens.append(("text", template[last:]))
    return tokens


def _parse(tokens: list[tuple], start: int = 0) -> tuple[list, int]:
    nodes = []
    index = start
    while index < len(tokens):
        kind = tokens[index][0]
        if kind in {"endif", "endeach"}:
            return nodes, index
        if kind in {"text", "var"}:
            nodes.append(tokens[index])
            index += 1
        elif kind == "if":
            body, close = _parse(tokens, index + 1)
            nodes.append(("if", tokens[index][1], body))
            index = close + 1
        else:
            body, close = _parse(tokens, index + 1)
            nodes.append(("each", tokens[index][1], body))
            index = close + 1
    return nodes, index


def _lookup(context: dict, path: str):
    if path == ".":
        return context.get(".", "")
    current = context
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _render_nodes(nodes: list, context: dict) -> str:
    out = []
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind == "var":
            value = _lookup(context, node[1])
            out.append("" if value is None else str(value))
        elif kind == "if":
            if _lookup(context, node[1]):
                out.append(_render_nodes(node[2], context))
        else:
            items = _lookup(context, node[1]) or []
            for item in items:
                child = dict(context)
                child["."] = item
                if isinstance(item, dict):
                    child.update(item)
                out.append(_render_nodes(node[2], child))
    return "".join(out)


def render(template: str, context: dict) -> str:
    nodes, _ = _parse(_tokenize(template))
    return _render_nodes(nodes, context)
