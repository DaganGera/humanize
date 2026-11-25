# humanize

An agent skill that rewrites or drafts prose so it reads as written by its human author, and checks the result against measured baselines of human writing.

It works in Claude Code and in any agent that reads `SKILL.md` skills. The measuring script is plain Python 3 with no dependencies.

## Why another humanizer

Most humanizers are lists of phrases to remove. Those lists go stale: in the papers measured for this skill, `underscores` went from 1% of papers in 2019 to 18% in 2024 and was already falling by 2026, while `rather than` went from 27% to 82%. A list written for one model generation misses the next, and can push text toward the new machine style.

This skill is built on three things that have held across model generations:

1. **Five properties, not phrases.** Machine-written text is unanchored (sentences with nothing checkable in them), compressed, even, staged, and carries the vocabulary of its period. Only the last changes quickly, and it is kept as dated data.
2. **Measurement against human writing of the same kind.** A research paper and a chat message are human in opposite ways. The script compares a text with a baseline for its kind and reports what is outside the human range, on either side.
3. **The author's content.** The largest lever found was the share of sentences tied to a number, source, name or example. A model cannot invent those, so the skill asks the author for them.

## Install

```sh
git clone https://github.com/DaganGera/humanize ~/.claude/skills/humanize
```

Then ask your agent to "humanize draft.tex", or type `/humanize draft.tex research-paper`.

## Profiles

| Profile | For | Built-in human baseline |
|---|---|---|
| `research-paper` | journal and conference papers, theses | 418 pre-2020 journal papers, per section |
| `blog-essay` | posts, essays, newsletters | 1,523 blog posts |
| `book-nonfiction` | non-fiction chapters | 1,319 news articles (nearest reference) |
| `book-fiction` | stories and novels | 1,395 fiction passages |
| `conversation` | chat replies, comments | 1,721 speech transcripts (rough) |
| `email-professional` | work email and messages | your own samples |
| `social-post` | social media posts | your own samples |
| `technical-docs` | READMEs and documentation | your own samples |
| `application` | cover letters, statements of purpose | your own samples |

A baseline built from your own writing beats any built-in one.

## The script

```sh
python3 scripts/humanize.py measure paper.tex                       # report by section
python3 scripts/humanize.py measure post.md --profile blog-essay
python3 scripts/humanize.py baseline my_old_writing/*.md -o voice.json
python3 scripts/humanize.py measure draft.md --baseline voice.json
python3 scripts/humanize.py check paper.tex paper.humanized.tex     # numbers, citations, refs, maths intact?
python3 scripts/humanize.py lexicon human.jsonl model.jsonl         # derive this year's over-used phrases
```

`measure` reads LaTeX, Markdown and plain text. Example output:

```
== intro · 840 words
   LOW  citations: 6.10 /1000w (human middle 90%: 7.95 to 40.26, median 21.53)
        -> few citations for this section type: name the source of each borrowed claim
   HIGH 'rather than': 1.19 /1000w (human middle 90%: 0.00 to 0.79, median 0.00)
        -> contrast framing: state what is the case
   · paragraph closes on commentary
       L57  Together, these results point to the value of depth-aware sampling.
```

The script does not detect AI. It says where a text sits against a set of human texts.

## What it can and cannot do about AI detectors

Tested on an open academic detector, with small samples (details in [docs/RESEARCH.md](docs/RESEARCH.md)):

- Model-written paper sections scored 0.88 (median). After rewriting with this skill and no author input: 0.68. Other prompts: 0.70 to 0.88. Human papers from 2018-19: 0.22.
- On a weaker detector the same rewrite went from 0.75 to 0.19, below the human median.
- The detector flagged about a quarter of the 2018-19 human papers.

So: rewording helps some, real content from the author helps more, and no score can be promised. Commercial detectors were not tested.

A detector score is also not a venue's rule. Most publishers allow AI assistance with writing and require disclosure. This skill does not change what you have to disclose.

## Keeping it current

The word lists in `data/lexicon.json` are dated because they expire. To refresh them, collect 50 or more texts from current models and 50 or more human texts of the same kind from before 2022, run the `lexicon` command, and add the result as a new entry. To add a profile, write `profiles/<name>.md` and build a baseline with the `baseline` command. Pull requests with new baselines, languages and profiles are welcome.

## Tests

```sh
python3 -m unittest discover -s tests
```

## Licence

MIT. The built-in baselines are summary statistics derived from open-access papers (Europe PMC) and the HAP-E corpus (MIT).
