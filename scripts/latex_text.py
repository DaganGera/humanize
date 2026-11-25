"""Extract prose from a LaTeX file as section-labelled paragraphs. Standard library only.

paragraphs(tex) -> list of {"section", "line", "text"}; citations become [C], maths [M].
"""
import re

DROP_ENVS = ("figure", "table", "equation", "align", "tabular", "algorithm", "lstlisting",
             "verbatim", "tikzpicture", "eqnarray", "gather", "multline", "thebibliography",
             "keywords", "displaymath", "array", "subfigure", "minipage")
KEEP_ARG = ("emph", "textbf", "textit", "texttt", "textsc", "underline", "mbox", "text",
            "textrm", "textsf", "uline", "textsuperscript", "textsubscript", "enquote")
DROP_CMD = ("label", "vspace", "hspace", "includegraphics", "caption", "bibliography",
            "bibliographystyle", "input", "include", "thanks", "footnote", "index", "pagestyle",
            "todo", "url", "href", "textcolor")


def _strip_comments(tex):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in tex.split("\n"))


def _braced(s, i):
    """Return index after the balanced {...} starting at s[i] == '{'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


def clean(s):
    s = re.sub(r"\\(?:citep?|citet|citealp|citeauthor|citeyear|parencite|textcite|autocite)\*?(?:\[[^\]]*\])*\{[^}]*\}", "[C]", s)
    s = re.sub(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{[^}]*\}", "1", s)
    s = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", " [M] ", s, flags=re.S)
    s = re.sub(r"(?<!\\)\$[^$]*?(?<!\\)\$|\\\(.*?\\\)", "[M]", s, flags=re.S)
    for _ in range(4):
        s = re.sub(r"\\(?:%s)\{([^{}]*)\}" % "|".join(KEEP_ARG), r"\1", s)
    # drop commands with their argument
    out, i = [], 0
    pat = re.compile(r"\\(?:%s)\*?(?:\[[^\]]*\])*(?=\{)" % "|".join(DROP_CMD))
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        i = _braced(s, m.end())
        while i < len(s) and s[i] == "{":
            i = _braced(s, i)
    s = "".join(out)
    s = s.replace("~", " ").replace("``", '"').replace("''", '"').replace("---", "—").replace("--", "–")
    s = re.sub(r"\\([%&#_$])", r"\1", s)
    s = re.sub(r"\\[,;:!> ]", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:)])", r"\1", s)
    return s.strip()


def paragraphs(tex):
    tex = _strip_comments(tex)
    m = re.search(r"\\begin\{document\}", tex)
    start = m.end() if m else 0
    body = tex[start:]
    base_line = tex[:start].count("\n") + 1
    # blank out dropped environments but keep line count
    for env in DROP_ENVS:
        body = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env),
                      lambda mm: "\n" * mm.group(0).count("\n"), body, flags=re.S)
    body = re.sub(r"\\end\{document\}.*", "", body, flags=re.S)
    out, section, buf, buf_line = [], "front", [], None
    lines = body.split("\n")

    def flush():
        nonlocal buf, buf_line
        if buf:
            t = clean(" ".join(buf))
            if len(t.split()) >= 12:
                out.append({"section": section, "line": buf_line, "text": t})
        buf, buf_line = [], None

    for n, ln in enumerate(lines):
        sm = re.search(r"\\(?:sub)*section\*?\{(.+?)\}\s*$", ln.strip())
        am = re.match(r"\s*\\begin\{abstract\}", ln)
        if sm or am:
            flush()
            if sm and ln.lstrip().startswith("\\section"):
                section = clean(sm.group(1))
            elif am:
                section = "Abstract"
                rest = ln[am.end():]
                if rest.strip():
                    buf, buf_line = [rest], base_line + n
            continue
        if re.match(r"\s*\\end\{abstract\}", ln):
            flush()
            section = "front"
            continue
        if not ln.strip():
            flush()
            continue
        if re.match(r"\s*\\(?:title|author|name|affil|maketitle|articletype|begin|end|item|bibliography|appendix|newcommand|renewcommand|setcounter)\b", ln):
            if re.match(r"\s*\\item\b", ln):
                flush()
                buf, buf_line = [re.sub(r"^\s*\\item\s*(\[[^\]]*\])?", "", ln)], base_line + n
            else:
                flush()
            continue
        if buf_line is None:
            buf_line = base_line + n
        buf.append(ln)
    flush()
    return out


if __name__ == "__main__":
    import sys, json
    ps = paragraphs(open(sys.argv[1], encoding="utf-8").read())
    for p in ps:
        print(json.dumps(p, ensure_ascii=False))
