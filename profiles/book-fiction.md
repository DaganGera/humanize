# Profile: fiction

Reference: 1,395 passages of human fiction (HAP-E corpus, public-domain novels and stories). The corpus is older fiction, so for a contemporary manuscript the author's own chapters are the right baseline: `H baseline ch1.md ch2.md -o voice.json`.

Fiction is the one profile where invented detail is the work. The rule against adding facts becomes: add nothing the author would not recognise as theirs, and change no event, name or line of plot.

## What human fiction looks like

- Sentence length varies more than in any written genre here (standard deviation about 62% of the mean of 20.5 words). A quarter of sentences are 10 words or fewer.
- Commas are heavy (78 per 1,000 words): clauses pile up in the long sentences.
- Plain verbs. `was`, `had`, `said`.
- Specific, odd, sometimes unlovely detail, and things left unexplained.

## How model-written fiction differs

- **Sameness of invention.** In 20,000 stories from four 2026 models, 88% shared 11 words; "lighthouse" appeared in half, "keeper" in 48%, and the name Elias in 26%, about 900 times its rate in published novels (Hamilton and Mimno, EMNLP 2026). The default name, job and setting are the tell. The names change by model; the sameness does not.
- **Explained feeling.** Emotions are named and then interpreted ("a mix of fear and hope"), and scenes end on a line of realisation.
- **Even rhythm**, grouped sensory details in threes, and trailing `-ing` clauses on action ("she turned, her heart pounding").
- **Abstract nouns as subjects**: silence, weight, memory, something that "shifted".

## Rewriting

1. Ask the author for the choices: the name, the place, the trade, the object in the room. Any detail the model supplied by default should be replaced by one the author chose.
2. Show the event and cut the sentence that says what it meant.
3. Let rhythm follow the action. Short where things happen fast. Long where a mind wanders.
4. Use `said`. Use `was`. Cut adverbs on dialogue tags.
5. End the scene on an action or a line of dialogue, not on a reflection.
6. Keep what is strange. Do not smooth dialect, fragments or a narrator's bad grammar.
