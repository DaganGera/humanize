#!/usr/bin/env python3
"""humanize: measure prose against human-written baselines. Standard library only.

  humanize.py measure FILE [--profile P] [--section S] [--baseline FILE] [--spots N] [--json]
  humanize.py check BEFORE AFTER            facts, numbers, citations and markup preserved?
  humanize.py baseline FILE... -o OUT.json  build a baseline from a writer's own texts
  humanize.py lexicon HUMAN AI [--top N]    derive over-used words from two sets of texts

FILE may be .tex, .md or plain text. Nothing here detects "AI"; it reports where a text
sits relative to a reference set of human writing, and where to look.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stylo  # noqa: E402
import latex_text  # noqa: E402
import lexicon as lexmod  # noqa: E402

DATA = os.path.join(os.path.dirname(HERE), "data")

# feature -> (label, unit, what to do when above the human range, when below)
REPORT = {
    "anchor_share": ("sentences tied to a number, citation, name or parenthesis", "share",
                     "", "too many sentences carry no checkable detail: add the fact from the author or cut the sentence"),
    "par_last_unanchored": ("paragraphs ending on a sentence with no checkable detail", "share",
                            "paragraphs close on commentary: end on the last fact", ""),
    "par_first_unanchored": ("paragraphs opening on a sentence with no checkable detail", "share",
                             "paragraphs open on a summary line: open on the first fact", ""),
    "sent_len_mean": ("mean sentence length", "words", "sentences run long: split the ones that hold two findings",
                      "sentences are clipped: join related facts with which/that/and"),
    "sent_len_cv": ("sentence-length variation (sd / mean)", "ratio", "", "sentence lengths are too even: let length follow content"),
    "sent_mid_share": ("sentences of 15-28 words", "share", "too many mid-length sentences in a row: mix long and short", ""),
    "sent_long_share": ("sentences of 35+ words", "share", "", "few long sentences: embed detail instead of starting new sentences"),
    "sent_short_share": ("sentences of 10 words or fewer", "share", "many short declaratives: merge them", ""),
    "par_words_cv": ("paragraph-length variation", "ratio", "", "paragraphs are all one size: let some be short, some long"),
    "part_tail": ("trailing -ing clauses (', highlighting...')", "/1000w", "end the sentence at the fact or start a new one with a subject", ""),
    "rather_than": ("'rather than'", "/1000w", "contrast framing: state what is the case", ""),
    "not_only": ("'not only'", "/1000w", "contrast framing: state both facts plainly", ""),
    "not_just": ("'not just/merely/simply'", "/1000w", "contrast framing: state the claim", ""),
    "neg_contrast": ("'is not X but Y' frames", "/1000w", "contrast framing: state Y", ""),
    "triad": ("three-item lists", "/1000w", "lists of exactly three: use the number of items the facts have", ""),
    "pair_and": ("'X and Y' word pairs", "/1000w", "paired near-synonyms: keep the one that carries meaning", ""),
    "promo": ("evaluative words (crucial, robust, key...)", "/1000w", "replace the adjective with the measurement or drop it", ""),
    "nominal": ("nominalisations (-tion, -ment, -ity)", "/1000w", "turn nouns back into verbs: 'we evaluated', not 'the evaluation of'", ""),
    "word_len_mean": ("mean word length", "letters", "vocabulary is heavy: prefer the short plain word", ""),
    "long_word_share": ("words of 10+ letters", "share", "vocabulary is heavy: prefer the short plain word", ""),
    "mattr50": ("word variety (types per 50 words)", "ratio", "too much synonym variation: repeat the plain term", ""),
    "copula": ("is/are/was/were/be", "/1000w", "", "plain 'is/are/was' are avoided: use them"),
    "passive": ("passive constructions", "/1000w", "", "passives are scarce for this kind of text: use them where the actor does not matter"),
    "w_of": ("'of'", "/1000w", "", "noun phrases are compressed: 'the accuracy of the model', not 'model accuracy'"),
    "w_the": ("'the'", "/1000w", "", "articles are being dropped by compression: restore full noun phrases"),
    "there_be": ("'there is/are'", "/1000w", "", ""),
    "paren": ("parentheses", "/1000w", "", "no parenthetical detail: put units, values and asides in parentheses"),
    "numerals": ("numbers", "/1000w", "", "few numbers: report the value instead of describing it"),
    "citations": ("citations", "/1000w", "", "few citations for this section type: name the source of each borrowed claim"),
    "first_person": ("we / our / I", "/1000w", "", "the authors are absent: say 'we' for what you did"),
    "hedge": ("hedges (may, might, seems...)", "/1000w", "stacked hedging: keep one hedge per uncertain claim", "no doubt expressed anywhere: mark what is uncertain"),
    "open_transition": ("sentences opening with a connective", "share", "connective at the start of too many sentences", "no sentence-initial connectives (However, Thus, In addition)"),
    "open_demonstrative": ("sentences opening with This/These", "share", "'This/These + summary noun' openers: name the thing", ""),
    "this_summary": ("'This approach / These findings' openers", "/1000w", "name the thing instead of pointing at it", ""),
    "while_mid": ("', while' joins", "/1000w", "two facts balanced with 'while': give each its own sentence", ""),
    "comma": ("commas", "/1000w", "", ""),
    "semicolon": ("semicolons", "/1000w", "semicolons staging a point: use a full stop", ""),
    "colon": ("colons", "/1000w", "colons staging a point: write the sentence straight", ""),
    "dash": ("dashes", "/1000w", "dashes as connectors: use commas, parentheses or a full stop", ""),
    "w_so": ("'so'", "/1000w", "'so' chains: vary with thus/therefore or a new sentence", ""),
    "w_these": ("'these'", "/1000w", "'these + noun' summarising: name the things", ""),
    "contraction": ("contractions", "/1000w", "", "no contractions for an informal text"),
    "question": ("questions", "/1000w", "", ""),
}

SPOTS = [
    ("trailing -ing clause", stylo.TAIL, lambda m: m.group(1) not in stylo.TAIL_SKIP),
    ("contrast frame", re.compile(r"\b(?:rather than|not only|not (?:just|merely|simply|solely)|as opposed to)\b", re.I), None),
    ("caution formula", re.compile(r"\b(?:should(?: not| therefore)? be (?:interpreted|regarded|viewed|taken|treated|read|understood) as|"
                                   r"does not (?:establish|imply|prove|by itself)|do not establish|it is (?:worth|important) (?:noting|to note))\b", re.I), None),
    ("summary opener", re.compile(r"^(?:Together|Collectively|Overall|Taken together|In summary|Importantly|Notably|Crucially)\b,?|"
                                  r"^(?:This|These) (?:findings?|results?|approach|design|observations?|patterns?) ", re.I), None),
    ("three-item list", stylo.REGEX_C["triad"], None),
]

SECTION_ALIASES = [
    (r"abstract", "intro"), (r"introduc|background|motivation", "intro"),
    (r"related|literature|prior work|state of the art", "related"),
    (r"result.*discuss|discuss.*result", "results_discussion"), (r"discuss", "discussion"),
    (r"conclu|summary|outlook|future", "conclusion"),
    (r"result|experiment|evaluat|finding|performance|analysis|ablation", "results"),
    (r"method|material|approach|proposed|model|design|data|procedure|framework|algorithm|setup|implementation", "methods"),
]


def section_kind(title):
    t = title.lower()
    for rx, kind in SECTION_ALIASES:
        if re.search(rx, t):
            return kind
    return None


def read_units(path):
    """Return [(section_title, [(line, paragraph_text)])] for .tex, .md or plain text."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if path.endswith(".tex"):
        units = collections.OrderedDict()
        for p in latex_text.paragraphs(raw):
            if p["section"] != "front":
                units.setdefault(p["section"], []).append((p["line"], p["text"]))
        return list(units.items())
    units, title, buf, start, fence = collections.OrderedDict(), "", [], None, False
    md = path.endswith((".md", ".markdown", ".mdx"))

    def flush():
        nonlocal buf, start
        t = " ".join(buf).strip()
        if md:
            t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
            t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
            t = re.sub(r"`[^`]*`", "X", t)
            t = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", t)
        if len(t.split()) >= 8:
            units.setdefault(title, []).append((start, t))
        buf, start = [], None

    for n, ln in enumerate(raw.split("\n"), 1):
        if md and ln.lstrip().startswith("```"):
            fence = not fence
            flush()
            continue
        if fence:
            continue
        if md and re.match(r"\s{0,3}#{1,6}\s", ln):
            flush()
            title = ln.strip("# \t")
            continue
        if not ln.strip():
            flush()
            continue
        if md:
            ln = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", ln)
            if re.match(r"\s*\|", ln):
                continue
        if start is None:
            start = n
        buf.append(ln.strip())
    flush()
    return list(units.items())


def load_baselines(profile, custom=None):
    if custom:
        b = json.load(open(custom, encoding="utf-8"))
        return b.get("sections", b), "custom baseline " + os.path.basename(custom)
    b = json.load(open(os.path.join(DATA, "baselines.json"), encoding="utf-8"))
    key = b["aliases"].get(profile, profile)
    if key not in b["profiles"]:
        return None, None
    return b["profiles"][key], b["sources"].get(key, key)


def gaps(feats, base):
    out = []
    for k, (label, unit, hi, lo) in REPORT.items():
        if k not in feats or k not in base:
            continue
        p5, p25, p50, p75, p95 = base[k]
        x = feats[k]
        spread = max((p75 - p25) / 1.349, (p95 - p5) / 3.29, abs(p50) * 0.08, 0.02 if unit in ("share", "ratio") else 0.15)
        if x > p95 and hi:
            out.append(((x - p95) / spread + 1, k, "high", hi))
        elif x < p5 and lo:
            out.append(((p5 - x) / spread + 1, k, "low", lo))
    out.sort(reverse=True)
    return out


def find_spots(paras, lex, limit):
    found = collections.OrderedDict()

    def add(kind, line, text):
        found.setdefault(kind, [])
        if len(found[kind]) < limit:
            found[kind].append((line, text.strip()[:110]))

    for line, par in paras:
        sents = stylo.split_sentences(par)
        for s in sents:
            for kind, rx, ok in SPOTS:
                m = rx.search(s)
                if m and (ok is None or ok(m)):
                    add(kind, line, s[max(0, m.start() - 45):m.end() + 45])
            low = s.lower()
            for ph, era in lex:
                if re.search(r"\b" + re.escape(ph) + r"\b", low):
                    add("lexicon (%s)" % era, line, "'%s' in: %s" % (ph, s[:70]))
        if len(sents) >= 3:
            def bare(x):
                return not (stylo.ANCHOR.search(x) or stylo.MIDCAP.search(x[1:]))
            if bare(sents[-1]):
                add("paragraph closes on commentary", line, sents[-1])
            if bare(sents[0]):
                add("paragraph opens on a summary line", line, sents[0])
        lens = [len(stylo.WORD.findall(s)) for s in sents]
        run = 1
        for a, b in zip(lens, lens[1:]):
            run = run + 1 if abs(a - b) <= 4 else 1
            if run == 4:
                add("four sentences of near-equal length", line, par[:90])
    return found


def load_lexicon():
    p = os.path.join(DATA, "lexicon.json")
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    return [(ph.lower(), e["era"]) for e in d["entries"] for ph in e["phrases"]]


def cmd_measure(a):
    units = read_units(a.file)
    if not units:
        sys.exit("no prose found in " + a.file)
    base_all, source = load_baselines(a.profile, a.baseline)
    lex = load_lexicon()
    paper = a.profile == "research-paper" and not a.baseline
    groups = collections.OrderedDict()
    if a.section or not paper:
        groups[a.section or "all"] = [p for _, ps in units for p in ps]
    else:
        for title, ps in units:
            groups.setdefault(section_kind(title) or "paper", []).extend(ps)
    result = []
    for kind, paras in groups.items():
        text = "\n\n".join(t for _, t in paras)
        feats = stylo.features(text)
        if not feats:
            continue
        base = None
        if base_all:
            base = base_all.get(kind) or base_all.get("all") or base_all.get("paper")
        result.append({"section": kind, "words": feats["n_words"], "features": feats,
                       "gaps": gaps(feats, base) if base else [], "base": base,
                       "spots": find_spots(paras, lex, a.spots)})
    if a.json:
        print(json.dumps([{"section": r["section"], "words": r["words"],
                           "gaps": [{"feature": k, "side": side, "value": round(r["features"][k], 3), "human": r["base"][k]}
                                    for _, k, side, _ in r["gaps"]],
                           "spots": r["spots"]} for r in result], indent=1))
        return
    print("reference: %s" % (source or "none for this profile; build one from the writer's own texts with `baseline`"))
    for r in result:
        print("\n== %s · %d words" % (r["section"], r["words"]))
        if r["words"] < 250:
            print("   (short text: rates are noisy, trust the hot spots more than the numbers)")
        if not r["gaps"]:
            print("   inside the human range on every measure" if r["base"] else "   no baseline; hot spots only")
        for sev, k, side, advice in r["gaps"][:a.top]:
            label, unit = REPORT[k][0], REPORT[k][1]
            b = r["base"][k]
            print("   %-4s %s: %.2f %s (human middle 90%%: %.2f to %.2f, median %.2f)\n        -> %s"
                  % (side.upper(), label, r["features"][k], unit, b[0], b[4], b[2], advice))
        for kind, items in r["spots"].items():
            print("   · %s" % kind)
            for line, text in items:
                print("       L%s  %s" % (line, text))


NUM = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?![\w])")


def facts(path):
    raw = open(path, encoding="utf-8").read()
    tex = path.endswith(".tex")
    if tex:
        raw = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in raw.split("\n"))
    f = {"numbers": collections.Counter(NUM.findall(raw)),
         "urls": collections.Counter(re.findall(r"https?://[^\s)}\]]+", raw)),
         "markers": collections.Counter(re.findall(r"\[[CM]\]|\[\d+(?:[,\-–]\s*\d+)*\]", raw))}
    if tex:
        cites = collections.Counter()
        for m in re.finditer(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]*)\}", raw):
            cites.update(k.strip() for k in m.group(1).split(","))
        f["citations"] = cites
        f["refs"] = collections.Counter(re.findall(r"\\(?:ref|eqref|autoref|cref|Cref|label)\{([^}]*)\}", raw))
        f["maths"] = collections.Counter(re.sub(r"\s+", "", m) for m in re.findall(r"(?<!\\)\$[^$]+\$|\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}", raw, flags=re.S))
        f["commands"] = collections.Counter(re.findall(r"\\(?:begin|end|section|subsection|subsubsection|includegraphics|caption|item)\b(?:\{[^}]*\})?", raw))
        prose = " ".join(p["text"] for p in latex_text.paragraphs(raw))
    else:
        prose = raw
    names = collections.Counter(m for m in re.findall(r"(?<![.!?]\s)(?<!^)\b(?:[A-Z][a-z]+[A-Z]\w*|[A-Z]{2,}[\w-]*|[A-Z][a-z]{2,}(?:[- ][A-Z][\w-]+)+)", prose))
    f["names"] = collections.Counter(set(names))
    f["words"] = len(prose.split())
    return f


def cmd_check(a):
    b, c = facts(a.before), facts(a.after)
    bad = 0
    for key in ("numbers", "citations", "refs", "maths", "commands", "urls", "markers", "names"):
        if key not in b:
            continue
        lost, added = b[key] - c.get(key, collections.Counter()), c.get(key, collections.Counter()) - b[key]
        if lost or added:
            soft = key == "names"
            bad += 0 if soft else 1
            print("%s %s:" % ("NOTE" if soft else "FAIL", key))
            if lost:
                print("   lost : " + ", ".join(sorted(lost.elements())[:40]))
            if added:
                print("   added: " + ", ".join(sorted(added.elements())[:40]))
        else:
            print("ok   %s (%d)" % (key, sum(b[key].values())))
    r = c["words"] / max(1, b["words"])
    print("%s length: %d -> %d words (x%.2f)" % ("NOTE" if not 0.8 <= r <= 1.25 else "ok  ", b["words"], c["words"], r))
    print("\nNumbers moved between sentences still pass this check: read each changed sentence against its source.")
    sys.exit(1 if bad else 0)


def cmd_baseline(a):
    chunks = []
    for path in a.files:
        paras = [t for _, ps in read_units(path) for _, t in ps]
        cur, n = [], 0
        for p in paras:
            cur.append(p)
            n += len(p.split())
            if n >= a.chunk:
                chunks.append("\n\n".join(cur))
                cur, n = [], 0
    feats = [f for f in (stylo.features(c) for c in chunks) if f]
    if len(feats) < 5:
        sys.exit("need at least %d words of the writer's own text (got %d usable chunks)" % (5 * a.chunk, len(feats)))

    def pct(xs, q):
        xs = sorted(xs)
        i = q * (len(xs) - 1)
        lo = int(i)
        hi = min(lo + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)

    base = {}
    for k in REPORT:
        xs = [f[k] for f in feats if k in f]
        if len(xs) >= 5:
            base[k] = [round(pct(xs, q), 4) for q in (0.05, 0.25, 0.5, 0.75, 0.95)]
    json.dump({"sections": {"all": base}, "chunks": len(feats), "files": [os.path.basename(f) for f in a.files]},
              open(a.out, "w", encoding="utf-8"), indent=1)
    print("baseline from %d chunks of about %d words -> %s" % (len(feats), a.chunk, a.out))


def cmd_lexicon(a):
    rows = lexmod.derive(lexmod.docs(a.human), lexmod.docs(a.ai), a.min_doc_share)

    def fmt(r):
        return "%s (%.0f%%->%.0f%%)" % (r[1], r[2] * 100, r[3] * 100)
    print("Share of documents containing the phrase, human -> other.\n\nOVER-USED by the second set:\n  " + "; ".join(fmt(r) for r in rows[::-1][:a.top]))
    print("\nUNDER-USED by the second set:\n  " + "; ".join(fmt(r) for r in rows[:a.top]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("file")
    m.add_argument("--profile", default="research-paper")
    m.add_argument("--section")
    m.add_argument("--baseline")
    m.add_argument("--top", type=int, default=12)
    m.add_argument("--spots", type=int, default=5)
    m.add_argument("--json", action="store_true")
    m.set_defaults(fn=cmd_measure)
    c = sub.add_parser("check")
    c.add_argument("before")
    c.add_argument("after")
    c.set_defaults(fn=cmd_check)
    b = sub.add_parser("baseline")
    b.add_argument("files", nargs="+")
    b.add_argument("-o", "--out", required=True)
    b.add_argument("--chunk", type=int, default=400)
    b.set_defaults(fn=cmd_baseline)
    x = sub.add_parser("lexicon")
    x.add_argument("human")
    x.add_argument("ai")
    x.add_argument("--top", type=int, default=60)
    x.add_argument("--min-doc-share", type=float, default=0.05)
    x.set_defaults(fn=cmd_lexicon)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
