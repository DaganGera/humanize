# Profile: research paper

For journal and conference papers, theses and technical reports. Reference: 417 open-access papers first published July 2018 to December 2019 in 12 journals across engineering, computing, life science, health and psychology. It was compared with 279 papers from 2024, 238 from 2026 and 400 sections written by current models. `H measure paper.tex` reports each section against its own baseline.

## What researchers' papers look like

Medians, with the middle 90% in brackets. Rates are per 1,000 words.

| | Introduction | Methods | Results | Discussion |
|---|---|---|---|---|
| Sentence length (words) | 25 (19-33) | 22 (17-30) | 23 (17-30) | 25 (19-32) |
| Sentences of 35+ words | 16% | 12% | 12% | 18% |
| Sentences of 10 words or fewer | 5% | 11% | 7% | 4% |
| Sentences tied to a number, citation, name or parenthesis | 75% | 78% | 83% | 71% |
| Citations | 22 (8-40) | 6 | 2 | 12 (0-26) |
| Numbers | 7 | 38 | 51 | 9 |
| Parentheses | 11 | 21 | 23 | 7 |
| Passives | 15 | 29 | 18 | 14 |
| `we`, `our` | 3 | 3 | 4 | 8 |
| Hedges (may, might, seems) | 8 | 4 | 7 | 15 |
| `of` | 41 | 37 | 38 | 40 |
| Sentences opening with `However,` `Moreover,` `Thus,` etc. | 16% | 7% | 12% | 20% |

This is not polished prose and should not be made into it. Human papers are long-sentenced, heavy with `of`, full of parentheses and `i.e.`, and they link sentences with the old formal connectives.

## How model-written papers differ

Measured in this corpus. The first group has held from 2024 models to late-2026 ones:

- **Fewer anchored sentences.** Paragraphs open on a summary line and close on a significance line. Numbers, citations and parentheses thin out.
- **Compression.** Mean word length went from 5.3 to 6.0 letters between 2019 and 2026 papers; `of` fell from 40 to 27 per 1,000 words, `the` from 76 to 59, `is/are/was/were` from 39 to 31. Nominalisations rose from 62 to 81.
- **Trailing `-ing` commentary.** 1.6 per 1,000 words in 2019, 4.5 in 2026.
- **The authors disappear.** `we` fell from 2.4 to 0.8 per 1,000 words.
- **Plain words go missing.** Share of papers using the phrase, 2019 then 2026: `in order to` 62%, 21%; `there is` 60%, 26%; `very` 69%, 37%; `i.e.` 53%, 26%; `might` 44%, 21%; `on the other hand` 40%, 15%; `by using` 35%, 7%.

The second group is period vocabulary and will change again:

- 2024 papers: `underscores` (1% of 2019 papers, 18% of 2024), `aligns with` (1%, 16%), `valuable insights` (1%, 16%), `leveraging` (2%, 18%). By 2026 `valuable insights` was back to 3%.
- 2026 papers: `rather than` (27% of 2019 papers, 82% of 2026), `be interpreted as` (4%, 36%), `across` (34%, 90%), `remains` (26%, 79%), `collectively, these` (0%, 13%), `does not establish` (0%, 9%).
- Late-2026 chat models writing from notes: shorter sentences than researchers write, almost no `Moreover,`/`Furthermore,`/`Thus,`, and `so`, `because`, `together, these`, `taken together`, `matters`, `this gap`, `is therefore` in their place.

Advice written against 2024 models ("shorten sentences, cut `Moreover`, prefer active voice, cut `in order to`") now moves a paper toward the 2026 machine register. Follow the measure, not the folklore.

## Rewriting a section

1. **Anchor or cut.** Go through the unanchored sentences the measure lists. For each, get the detail from the author (the value, the source, the dataset, the figure, the reason) or delete the sentence. Open a paragraph on its first fact and end it on its last.
2. **Report, do not interpret.** Say what was done and found, with the actor or source: `we trained`, `was measured`, `X et al. reported that`, `as can be seen in Table 2`. Put the number in the sentence that makes the claim. Interpretation belongs in the Discussion and carries a real hedge (`may`, `might be due to`, `seems`).
3. **Uncompress.** `the accuracy of the model on the test set`, not `test-set model accuracy`. Use `is`, `was`, `has`, `there are`. Turn `the evaluation of X was performed` into `we evaluated X` or `X was evaluated`.
4. **Let sentences be long where the content is connected.** Join related facts with `which`, `that`, `and`, `where`, and put side detail in parentheses (units, settings, `i.e.`, `e.g.`, `see Fig. 3`). Short sentences are rare in papers; do not chop.
5. **Link sentences the way papers do.** `However,` `Moreover,` `In addition,` `Thus,` `Therefore,` `On the other hand,` `For example,` at the start of roughly one sentence in six, more in the Discussion, fewer in Methods.
6. **Remove staging.** `rather than`, `not only`, `not X but Y`; `should be interpreted as`, `does not establish`; trailing `-ing` clauses; `This/These + summary noun` openers; colons and semicolons that set up a point; lists of exactly three; evaluative adjectives (`robust`, `comprehensive`, `notable`, `effective`) standing where a measurement should be.
7. **Repeat the technical term.** Do not vary it with synonyms.

## By section

- **Abstract.** One paragraph, numbers included, no significance sentence at the end.
- **Introduction.** The most citation-dense section. Each claim about the field names its source. State the gap as a fact about prior work, then what this paper does.
- **Related work.** Organised by what each work did, with the author as subject (`Liu et al. proposed`), and the specific limit that matters here.
- **Methods.** Passive is normal. Exact values, settings and versions. No motivation paragraphs between steps.
- **Results.** The most numeric section: a value, its comparison, and where to see it. No adjectives for the size of an effect without the size.
- **Discussion.** Where hedges and `we` belong. Limitations stated as specific facts about this study (the sample, the dataset, what was not measured), not as a formula.
- **Conclusion.** What was done and found, with the main numbers. Future work only if there is a concrete plan.

## Leave alone

LaTeX commands, citation keys, labels, maths, tables, figure captions unless asked, quoted text, and standard field phrases even when a word list flags them (`robust` for a statistical estimator, `significant` with a p-value). Follow the journal's spelling and its rule on first person. If the author's first language shows in the phrasing and the meaning is clear, that is their voice; fix errors, do not polish it away.

## Example

An invented illustration. Model-written, from the authors' notes:

> Soil enzyme activity is a sensitive indicator of soil health, yet its response to long-term fertilisation remains poorly understood. Our study addresses this gap by examining dehydrogenase activity across two depths, enabling a more nuanced picture of microbial function. Together, these results highlight the importance of organic carbon, underscoring the need for depth-aware sampling.

Rewritten after asking the authors for the figures:

> The activity of dehydrogenases is often used as an indicator of the biological state of the soil [C], but there are few data on how it changes with depth after long-term fertilisation. In this study, dehydrogenase activity was measured in soil samples taken from two layers (0-20 cm and 20-40 cm) at six points of a field which had been fertilised for 28 years. The activity in the top layer ranged from 0.092 to 0.164 mg TPF per kg in 24 h (mean 0.127) and was higher than in the 20-40 cm layer (mean 0.106). The highest activity was found at point 2, which may be related to the organic carbon content being higher there than at the other points (Table 4).
