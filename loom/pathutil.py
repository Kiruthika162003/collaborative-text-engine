"""Path util: POSIX-style path manipulation, purely lexical, no filesystem touched.

Manipulating slash-separated paths is a set of small operations
a caller needs constantly, and this provides them without
reaching for the standard library and without touching a real
filesystem, so they work the same on any platform and on paths
that name nothing. Joining follows the rule everyone expects: a
part that begins with a slash is absolute and resets the join,
otherwise parts are glued with a single slash however many the
inputs had. Normalizing is the careful one, resolving the dot
and dot-dot segments lexically, a dot dropped and a dot-dot
popping the previous segment, with the two edge rules that trip
a naive version: a dot-dot at the root of an absolute path stays
at the root rather than escaping above it, and a dot-dot that
would escape a relative path is kept, because dot-dot from an
unknown current directory really does go up and dropping it
would resolve to the wrong place. The resolution is purely
lexical, stated plainly: it does not follow symlinks or check
what exists, because those need a filesystem this deliberately
does not consult, so a normalized path is the path the segments
describe, not necessarily the file they would reach through
links. Splitting the extension takes the last dot of the final
segment and treats a leading dot as part of the name rather
than an extension, so a dotfile keeps its whole name and only a
real suffix is separated, which is the behaviour a caller
naming files by extension depends on.
"""

from __future__ import annotations


def join(*parts: str) -> str:
    result = ""
    for part in parts:
        if not part:
            continue
        if part.startswith("/"):
            result = part
        elif not result or result.endswith("/"):
            result += part
        else:
            result += "/" + part
    return result


def normalize(path: str) -> str:
    absolute = path.startswith("/")
    segments: list[str] = []
    for segment in path.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if segments and segments[-1] != "..":
                segments.pop()
            elif not absolute:
                segments.append("..")
        else:
            segments.append(segment)
    joined = ("/" if absolute else "") + "/".join(segments)
    return joined or ("/" if absolute else ".")


def dirname(path: str) -> str:
    if "/" not in path:
        return ""
    head = path.rsplit("/", 1)[0]
    return head or "/"


def basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def split_ext(path: str) -> tuple[str, str]:
    name = basename(path)
    dot = name.rfind(".")
    if dot <= 0:
        return (path, "")
    cut = len(path) - len(name) + dot
    return (path[:cut], path[cut:])
