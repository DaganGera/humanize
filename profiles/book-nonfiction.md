# Profile: non-fiction book

Reference: no book corpus is built in. The nearest baseline is 1,319 human news articles (HAP-E corpus), which share the job of explaining real events to a general reader. A chapter the author wrote unaided is a better reference: `H baseline chapter1.md chapter2.md -o voice.json`.

## What human explanatory prose looks like

- Sentences average 19 words, with one in five at 10 words or fewer.
- Three quarters of sentences carry a name, number, date or quotation. Explanation runs on particulars: who, where, when, how much.
- Contractions appear (about 15 per 1,000 words). Dashes are used (about 4 per 1,000).
- An argument builds across chapters. A paragraph assumes what earlier ones established.

## How model-written chapters differ

The cross-genre pattern holds (even sentence lengths, longer words, nominalisation, trailing `-ing` clauses, avoided `is/was`), plus three book-specific habits: every section is self-contained and re-explains its terms; chapters open with a scene-setting generality and close with a paragraph of takeaways; and examples are generic ("a manager at a large company") where a real book names the person and the year.

## Rewriting

1. Ask for the particulars: the real case, the name, the date, the figure, the source. Replace each generic example with one or cut it.
2. Let the chapter lean on the book. Remove re-definitions and recaps of earlier chapters unless the author wants them.
3. Keep the author's stance. If they think something is wrong, the sentence says so without a balancing clause.
4. Carry the argument with `so`, `because`, `but`, `then`. Avoid signposts that announce what the section will do.
5. End sections on the last piece of content. No takeaway lists unless the book's format has them.
6. Remove staging and period vocabulary as in `SKILL.md`.

Leave alone: quotations, references, epigraphs, the author's recurring terms.
