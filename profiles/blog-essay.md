# Profile: blog post, essay, newsletter

Reference: 1,523 human blog posts (HAP-E corpus), compared with continuations of the same posts by GPT-4o and Llama 3 (2024 models). `H measure post.md --profile blog-essay`.

## What human posts look like

- Sentences average 17 words and vary a lot (standard deviation about 60% of the mean). Three in ten are 10 words or fewer, and many have no comma at all.
- First person is everywhere: 45 `I/we/my/our` per 1,000 words. Contractions: 16 per 1,000. A question about every 500 words.
- Words are short (4.2 letters on average) and repeat. `is`, `was`, `so`, `because`, `then`, `very`, `have` are common.
- Fewer than half the sentences carry a number or a name, so anchoring matters less here than in a paper. What anchors a post is the writer: what happened to them, what they think, what they are unsure of.

## How model-written posts differ

In every genre tested, including this one: sentence lengths bunch into the 15-28 word band (effect size about 1.5 standard deviations), sentences with no comma nearly vanish, words get longer, nouns replace verbs, `is/was` are avoided, trailing `-ing` clauses multiply, and `so`, `because`, `then` and `very` thin out. Opinions get balanced into "on one hand, on the other" and the ending restates the post.

## Rewriting

1. Ask the writer what they actually think and what happened. A post with no position and no event has nothing to humanize.
2. One point per sentence where the point is simple. Let a short sentence stand with no comma. Let a long one run when the thought does.
3. Say `I`. Use contractions if the writer does. Keep their asides, their doubt and their bad jokes.
4. Use the plain word and repeat it. `Use`, not `leverage`; `shows`, not `underscores`.
5. Cut the opening that announces the topic and the closing that summarises it. Start where the story or the claim starts and stop when it is told.
6. Remove staging: `not X but Y`, `here's the thing`, rhetorical questions answered at once, one-line paragraphs for effect, lists of three, bold lead-ins on every bullet.

Leave alone: quotes, code, links, the writer's dialect and spelling.
