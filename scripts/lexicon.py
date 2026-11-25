"""Find words and phrases one set of texts over-uses relative to another.
Used by `humanize.py lexicon HUMAN AI`.
Each input: a JSONL file with a "text" field per line, or a folder/plain file (blank-line separated docs).
Scores by document frequency so one long document cannot dominate.
"""
import json, math, re, sys, collections, os

W = re.compile(r"[a-z][a-z'’\-]*")

def docs(path):
    if path.endswith(".jsonl"):
        return [json.loads(l)["text"] for l in open(path, encoding="utf-8") if l.strip()]
    if os.path.isdir(path):
        return [open(os.path.join(path, f), encoding="utf-8").read() for f in sorted(os.listdir(path))]
    return [d for d in re.split(r"\n\s*\n\s*\n", open(path, encoding="utf-8").read()) if d.strip()]

def grams(text, nmax=3):
    toks = W.findall(text.lower())
    out = set(toks)
    for n in range(2, nmax + 1):
        out |= {" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)}
    return out

def derive(human, ai, min_share=0.03, nmax=3):
    dh, da = collections.Counter(), collections.Counter()
    for t in human: dh.update(grams(t, nmax))
    for t in ai: da.update(grams(t, nmax))
    nh, na = len(human), len(ai)
    rows = []
    for w in set(dh) | set(da):
        h, a = dh[w], da[w]
        if max(h / nh, a / na) < min_share: continue
        lo = math.log((a + 1) / (na - a + 1)) - math.log((h + 1) / (nh - h + 1))
        rows.append((lo, w, h / nh, a / na))
    rows.sort()
    return rows

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 60
    ms = float(sys.argv[sys.argv.index("--min-doc-share") + 1]) if "--min-doc-share" in sys.argv else 0.03
    rows = derive(docs(args[0]), docs(args[1]), ms)
    f = lambda r: f"{r[1]} ({r[2]*100:.0f}%→{r[3]*100:.0f}%)"
    print("UNDER-USED by the second set (share of documents, first→second):\n  " + "; ".join(f(r) for r in rows[:top]))
    print("OVER-USED by the second set:\n  " + "; ".join(f(r) for r in rows[::-1][:top]))
