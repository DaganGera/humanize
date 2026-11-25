"""Style features for prose. Standard library only.

features(text) -> dict of floats. Text is plain prose with paragraphs separated by
blank lines. Citation and maths placeholders ([C], [M]) are tolerated.
"""
import math
import re
import statistics as st

ABBR = r"(?:e\.g|i\.e|et al|etc|vs|cf|Fig|Figs|Eq|Eqs|Ref|Refs|Tab|Sec|No|Dr|Mr|Mrs|Ms|Prof|approx|resp|ca|al|St|Inc|Ltd|Co|viz|wrt)"
_PROTECT = re.compile(r"\b" + ABBR + r"\.", re.I)
_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]*[A-Z0-9])")
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")

TRANSITIONS = {
    "however", "moreover", "furthermore", "additionally", "therefore", "thus", "consequently",
    "hence", "notably", "specifically", "importantly", "overall", "finally", "similarly",
    "conversely", "nevertheless", "nonetheless", "meanwhile", "accordingly", "likewise", "indeed",
    "interestingly", "first", "second", "third", "firstly", "secondly", "thirdly", "lastly",
    "subsequently", "collectively", "together", "crucially", "ultimately", "instead", "also",
    "besides", "still", "yet", "then", "next", "here", "further", "alternatively", "generally",
}
TRANS_PHRASES = ("in addition", "in contrast", "in particular", "for example", "for instance",
                 "as a result", "on the other hand", "to this end", "in summary", "in conclusion",
                 "in other words", "as such", "in this way", "in fact", "by contrast", "as shown",
                 "taken together", "in practice", "in general", "at the same time", "to address")
FORMAL_ADD = {"moreover", "furthermore", "additionally", "notably", "importantly", "consequently",
              "specifically", "crucially", "collectively", "ultimately", "overall"}
SUBORD = {"although", "while", "when", "if", "since", "because", "as", "whereas", "once", "unless",
          "after", "before", "given", "despite", "though", "where", "until"}
PREP = {"in", "for", "to", "by", "with", "at", "on", "from", "through", "during", "among",
        "between", "under", "within", "across", "based", "compared", "unlike", "like", "due",
        "using", "following", "according", "over", "beyond", "without", "of", "into", "upon"}
HEDGES = {"may", "might", "could", "would", "likely", "possibly", "perhaps", "probably",
          "presumably", "approximately", "roughly", "somewhat", "relatively", "generally",
          "usually", "often", "sometimes", "almost", "apparently", "seemingly", "plausibly",
          "arguably", "largely", "mostly", "partly", "fairly", "rather", "quite", "typically",
          "unlikely", "possible", "potentially"}
HEDGE_STEMS = ("suggest", "appear", "seem", "tend", "indicat", "assum", "estimat", "speculat",
               "expect", "believ")
PLAIN_BOOST = {"clearly", "obviously", "certainly", "definitely", "always", "never", "must",
               "very", "much", "far", "extremely", "really", "simply", "just", "only", "even",
               "especially", "particularly", "indeed", "actually", "exactly", "entirely"}
# Words that every generation of chat model has over-used when dressing a claim.
PROMO = {"crucial", "pivotal", "vital", "essential", "critical", "key", "significant",
         "significantly", "comprehensive", "robust", "novel", "seamless", "seamlessly",
         "innovative", "cutting-edge", "state-of-the-art", "notable", "notably", "remarkable",
         "remarkably", "substantial", "substantially", "valuable", "meaningful", "holistic",
         "nuanced", "intricate", "multifaceted", "promising", "effective", "effectively",
         "efficient", "efficiently", "powerful", "superior", "enhanced", "advanced", "diverse",
         "dynamic", "rich", "profound", "transformative", "unprecedented", "paramount",
         "indispensable", "invaluable", "noteworthy", "compelling", "rigorous", "meticulous",
         "meticulously", "scalable", "versatile", "practical", "dependable", "reliable",
         "landscape", "realm", "tapestry", "testament", "interplay", "insights", "challenges",
         "advancements", "implications", "underscore", "underscores", "underscoring",
         "highlight", "highlights", "highlighting", "showcase", "showcases", "showcasing",
         "leverage", "leverages", "leveraging", "foster", "fosters", "fostering", "enhance",
         "enhances", "enhancing", "facilitate", "facilitates", "facilitating", "delve", "delves",
         "emphasize", "emphasizes", "emphasizing", "ensure", "ensures", "ensuring", "enable",
         "enables", "enabling", "empower", "empowers", "streamline", "harness", "harnessing",
         "elucidate", "exhibits", "exhibit", "demonstrates", "demonstrate", "demonstrating",
         "encompasses", "encompassing", "align", "aligns", "prioritize", "optimize", "boasts",
         "garner", "bolster", "bolstered", "offering", "offers", "addressing", "paving"}
TAIL_SKIP = {"including", "according", "during", "regarding", "concerning", "following",
             "depending", "excluding", "notwithstanding", "considering", "nothing", "something",
             "anything", "everything", "king", "thing", "string", "spring", "ring", "being",
             "interesting", "interestingly", "training", "testing", "learning", "processing",
             "imaging", "engineering", "sensing", "modeling", "modelling", "sampling",
             "building", "setting", "understanding", "meaning", "finding", "findings"}
NOMINAL = re.compile(r"(?:tion|tions|sion|sions|ment|ments|ness|ity|ities|ance|ances|ence|ences)$")
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|been|being|be)\s+(?:\w+ly\s+)?(?:\w{3,}ed|shown|given|known|found|made|"
    r"done|seen|taken|built|drawn|chosen|written|held|kept|set|put|run|fed|led|left|sent|split)\b", re.I)

REGEX = {
    "part_tail": None,  # handled separately
    "not_only": r"\bnot only\b",
    "rather_than": r"\brather than\b",
    "not_just": r"\bnot (?:just|merely|simply|solely)\b",
    "neg_contrast": r"\b(?:is|are|was|were|does|do|did)(?: not|n[’']t)\b[^.;:]{3,70}?[,;]?\s+but\b",
    "ranging_from": r"\brang(?:ing|es|e) from\b",
    "plays_role": r"\bplay(?:s|ed|ing)? an? [\w-]+ role\b",
    "it_is_adj": r"\bit is (?:worth|important|essential|crucial|noteworthy|imperative|vital|evident|clear)\b",
    "in_order_to": r"\bin order to\b",
    "as_well_as": r"\bas well as\b",
    "due_to": r"\bdue to\b",
    "there_be": r"\bthere (?:is|are|was|were|exists?)\b",
    "fact_that": r"\bthe fact that\b",
    "range_of": r"\ba (?:wide |broad |diverse |large )?(?:range|variety|number|array|spectrum) of\b",
    "in_terms_of": r"\bin terms of\b",
    "respectively": r"\brespectively\b",
    "eg_ie": r"\b(?:e\.g\.|i\.e\.)",
    "et_al": r"\bet al\b",
    "to_purpose_start": r"(?:^|(?<=[.!?]\s))To [a-z]+ (?:this|these|the|such|that)\b",
    "this_summary": r"(?:^|(?<=[.!?]\s))(?:This|These) (?:approach|method|finding|findings|result|results|"
                    r"suggests?|indicates?|highlights?|demonstrates?|shows?|underscores?|ensures?|"
                    r"enables?|allows?|makes?|means|design|strategy|observation|pattern|behaviou?r|"
                    r"improvement|gap|limitation|is because|is particularly|is especially)\b",
    "by_ing": r"\b[Bb]y [a-z]+ing\b",
    "while_mid": r",\s+while\b",
    "whereas": r"\bwhereas\b",
    "which": r"\bwhich\b",
    "that": r"\bthat\b",
    "such_as": r"\bsuch as\b",
    "including": r"\bincluding\b",
    "can": r"\bcan\b",
    "we_verb": r"\b[Ww]e (?:[a-z]+ly )?[a-z]+",
    "colon_list": r":\s+(?:\(?[1ia]\)|\w+[^.]{0,60},[^.]{0,60},)",
    "semicolon": r";",
    "paren": r"\(",
    "dash": r"—|–(?=\s)|\s-\s|--",
    "question": r"\?",
    "quote": r"[\"“”]",
    "percent": r"%",
    "contraction": r"\b\w+(?:n[’']t|[’'](?:s|re|ve|ll|d|m))\b",
    "triad": r"\b[\w-]+(?:\s[\w-]+){0,2},\s[\w-]+(?:\s[\w-]+){0,2},?\s(?:and|or)\s[\w-]+",
    "pair_and": r"\b(?:both\s)?[a-z]{5,}\sand\s[a-z]{5,}\b",
}
REGEX_C = {k: re.compile(v) for k, v in REGEX.items() if v}
ANCHOR = re.compile(r"\d|\[C\]|\[M\]|\(|\b[A-Z]{2,}|\b(?:Fig|Table|Eq|Section|Figure|Equation|Algorithm)\b|%")
MIDCAP = re.compile(r"(?<![.!?]\s)\b[A-Z][a-z]{2,}")
TAIL = re.compile(r",\s+(?:thereby |thus |hence |further |ultimately |effectively |potentially )?([a-z]+ing)\b")
LEXKEYS = ["but", "however", "although", "though", "yet", "because", "since", "so", "thus",
           "therefore", "hence", "moreover", "furthermore", "additionally", "also", "while",
           "the", "of", "and", "is", "are", "was", "were", "has", "have", "this", "these", "it",
           "our", "we", "very", "more", "most", "not", "no", "can", "will", "been", "by", "with",
           "for", "to", "in", "on", "as", "an", "a", "or", "if", "then", "than", "such", "both",
           "each", "all", "some", "many", "several", "various", "different", "new", "used",
           "using", "based", "proposed", "show", "shows", "shown", "showed", "use", "uses"]


def split_sentences(par):
    p = _PROTECT.sub(lambda m: m.group(0).replace(".", "․"), par)
    return [s.replace("․", ".").strip() for s in _SPLIT.split(p) if s.strip()]


def _cv(xs):
    return st.pstdev(xs) / st.mean(xs) if len(xs) > 1 and st.mean(xs) else 0.0


def _first_class(sent):
    low = sent.lower().lstrip("\"'([“")
    for ph in TRANS_PHRASES:
        if low.startswith(ph):
            return "transition", ph
    m = WORD.match(low)
    if not m:
        return "other", "#"
    w = m.group(0)
    if w in TRANSITIONS and (low[len(w):len(w) + 1] == "," or w in FORMAL_ADD or w in ("however", "thus", "therefore", "hence")):
        return "transition", w
    if w in ("this", "these", "such", "those", "that"):
        return "demonstrative", w
    if w in ("we", "our", "i", "my"):
        return "first_person", w
    if w in ("the", "a", "an"):
        return "article", w
    if w in ("it", "there"):
        return "expletive", w
    if w in SUBORD:
        return "subordinator", w
    if w in PREP:
        return "preposition", w
    if w.endswith("ing") and len(w) > 5:
        return "ing", w
    return "other", w


def features(text):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sents_by_par = [split_sentences(p) for p in paras]
    sents = [s for ss in sents_by_par for s in ss]
    words = [w.lower() for w in WORD.findall(text) if w not in ("C", "M")]
    n = len(words)
    f = {}
    if n < 50 or len(sents) < 3:
        return f
    k = 1000.0 / n
    slen = [len(WORD.findall(s)) for s in sents]
    slen = [x for x in slen if x > 0]
    ns = len(slen)
    f["n_words"] = n
    f["sent_len_mean"] = st.mean(slen)
    f["sent_len_sd"] = st.pstdev(slen)
    f["sent_len_cv"] = _cv(slen)
    srt = sorted(slen)
    f["sent_len_p10"] = srt[int(0.1 * (ns - 1))]
    f["sent_len_p90"] = srt[int(0.9 * (ns - 1))]
    f["sent_short_share"] = sum(x <= 10 for x in slen) / ns
    f["sent_long_share"] = sum(x >= 35 for x in slen) / ns
    f["sent_mid_share"] = sum(15 <= x <= 28 for x in slen) / ns
    f["sent_adj_diff"] = (st.mean(abs(a - b) for a, b in zip(slen, slen[1:])) / st.mean(slen)) if ns > 2 else 0
    plen = [len(WORD.findall(p)) for p in paras]
    spp = [len(s) for s in sents_by_par]
    f["par_words_mean"] = st.mean(plen)
    f["par_words_cv"] = _cv(plen)
    f["par_sents_mean"] = st.mean(spp)
    f["par_sents_cv"] = _cv(spp)
    # sentence openers
    classes, firsts = [], []
    for s in sents:
        c, w = _first_class(s)
        classes.append(c)
        firsts.append(w)
    for c in ("transition", "demonstrative", "first_person", "article", "expletive",
              "subordinator", "preposition", "ing", "other"):
        f["open_" + c] = classes.count(c) / len(sents)
    cnt = {}
    for w in firsts:
        cnt[w] = cnt.get(w, 0) + 1
    ent = -sum(v / len(firsts) * math.log2(v / len(firsts)) for v in cnt.values())
    f["open_entropy"] = ent / math.log2(len(firsts)) if len(firsts) > 1 else 0
    f["open_repeat"] = sum(a == b for a, b in zip(firsts, firsts[1:])) / max(1, len(firsts) - 1)
    f["open_formal_add"] = sum(w in FORMAL_ADD for w in firsts) / len(sents)
    # punctuation and constructions
    f["comma"] = text.count(",") * k
    f["colon"] = len(re.findall(r":(?=\s)", text)) * k
    for name, rx in REGEX_C.items():
        f[name] = len(rx.findall(text)) * k
    f["part_tail"] = sum(1 for m in TAIL.finditer(text) if m.group(1) not in TAIL_SKIP) * k
    f["commas_per_sent"] = text.count(",") / len(sents)
    f["sent_no_comma"] = sum("," not in s for s in sents) / len(sents)
    f["sent_colon"] = sum(":" in s for s in sents) / len(sents)
    f["sent_semicolon"] = sum(";" in s for s in sents) / len(sents)
    f["sent_paren"] = sum("(" in s for s in sents) / len(sents)
    pset = sum(bool(re.search(p, text)) for p in (r";", r":\s", r"\(", r"—|–\s|\s-\s", r"\?", r"[\"“]"))
    f["punct_variety"] = pset
    # lexical
    wc = {}
    for w in words:
        wc[w] = wc.get(w, 0) + 1
    for key in LEXKEYS:
        f["w_" + key] = wc.get(key, 0) * k
    f["hedge"] = (sum(wc.get(w, 0) for w in HEDGES) + sum(v for w, v in wc.items() if w.startswith(HEDGE_STEMS))) * k
    f["plain_boost"] = sum(wc.get(w, 0) for w in PLAIN_BOOST) * k
    f["promo"] = sum(wc.get(w, 0) for w in PROMO) * k
    f["first_person"] = sum(wc.get(w, 0) for w in ("we", "our", "us", "i", "my", "ours")) * k
    f["copula"] = sum(wc.get(w, 0) for w in ("is", "are", "was", "were", "be", "been", "being")) * k
    f["passive"] = len(PASSIVE.findall(text)) * k
    f["nominal"] = sum(v for w, v in wc.items() if len(w) > 6 and NOMINAL.search(w)) * k
    f["ing_words"] = sum(v for w, v in wc.items() if len(w) > 5 and w.endswith("ing")) * k
    f["ly_adverbs"] = sum(v for w, v in wc.items() if len(w) > 4 and w.endswith("ly")) * k
    f["word_len_mean"] = sum(len(w) for w in words) / n
    f["long_word_share"] = sum(len(w) >= 10 for w in words) / n
    f["numerals"] = len(re.findall(r"\b\d[\d.,]*\b", text)) * k
    f["citations"] = text.count("[C]") * k
    f["maths"] = text.count("[M]") * k
    f["acronyms"] = len(re.findall(r"\b[A-Z]{2,}[a-z]?\b", text)) * k
    # specificity: sentences anchored to something checkable
    anch = [bool(ANCHOR.search(x)) or bool(MIDCAP.search(x[1:])) for x in sents]
    f["anchor_share"] = sum(anch) / len(sents)
    lasts, firsts_p, lshort = [], [], []
    for ss in sents_by_par:
        if len(ss) >= 3:
            lasts.append(not (ANCHOR.search(ss[-1]) or MIDCAP.search(ss[-1][1:])))
            firsts_p.append(not (ANCHOR.search(ss[0]) or MIDCAP.search(ss[0][1:])))
            ls = [len(WORD.findall(x)) for x in ss]
            lshort.append(ls[-1] <= 0.6 * (sum(ls) / len(ls)))
    if len(lasts) >= 3:
        f["par_last_unanchored"] = sum(lasts) / len(lasts)
        f["par_first_unanchored"] = sum(firsts_p) / len(firsts_p)
        f["par_last_short"] = sum(lshort) / len(lshort)
    win = 50
    if n >= win:
        f["mattr50"] = st.mean(len(set(words[i:i + win])) / win for i in range(0, n - win + 1, 10))
    return f


if __name__ == "__main__":
    import json, sys
    print(json.dumps(features(open(sys.argv[1], encoding="utf-8").read()), indent=1))
