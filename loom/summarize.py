"""Summarize: pick the sentences that carry the document's own frequent words.

Extractive summary is selection, not composition: it does
not write a shorter document, it chooses sentences from the
one that exists, and the sentences it chooses are the ones
densest in the words the document returns to most. This
scores each sentence by the summed frequency of its content
words, the same keyword frequencies the keywords module
computes, and takes the highest scoring few, returned in
reading order so the excerpt still reads forward rather than
in a jumble of rank. The method's bias is stated because it
is real: summing frequencies favours long sentences and
sentences that repeat a frequent word, so a keyword-stuffed
tangent can outscore the crisp thesis it buried, and this
picks by density, not by insight it does not have. It is
offered for what it is, a fast way to see which sentences a
document leans on, useful for a first pass and wrong to
trust as the document's actual point, which only a reader
can name. A one-sentence document summarizes to that
sentence, and a document with no sentences summarizes to
nothing, both without ceremony, because a summary that
invented a point for an empty page would be composing after
all, the one thing this promises not to do.
"""

from __future__ import annotations

from loom.keywords import WORD, frequencies
from loom.sentences import Sentence, sentences
from loom.weave import Weave


def scored(weave: Weave) -> list[tuple[Sentence, int]]:
    freq = frequencies(weave)
    result = []
    for sentence in sentences(weave):
        words = [
            match.group(0).lower() for match in WORD.finditer(sentence.text)
        ]
        score = sum(freq.get(word, 0) for word in words)
        result.append((sentence, score))
    return result


def summarize(weave: Weave, count: int = 3) -> list[str]:
    ranked = scored(weave)
    if not ranked:
        return []
    by_score = sorted(
        ranked, key=lambda pair: (-pair[1], pair[0].ordinal)
    )
    chosen = {sentence.ordinal for sentence, _score in by_score[:count]}
    return [
        sentence.text
        for sentence, _score in ranked
        if sentence.ordinal in chosen
    ]


def report(weave: Weave, count: int = 3) -> str:
    picked = summarize(weave, count)
    if not picked:
        return "nothing to summarize; the document has no sentences"
    return "\n".join(
        [
            f"summary, {len(picked)} sentence(s) by keyword density:",
            *(f"  {text}" for text in picked),
            "selection, not composition; density is not insight",
        ]
    )
