# Research notes

What this skill is built on: published studies, and measurements made for it in November 2026. Sample sizes are small in places and are stated so that the limits are visible.

## 1. Corpora measured for this skill

| Set | Size | Source |
|---|---|---|
| Human papers, pre-LLM | 418 papers | Europe PMC open-access full text, first published July 2018 to December 2019, 12 journals (Sensors, PLoS One, Scientific Reports, Heliyon, PeerJ Computer Science, Frontiers in Psychology, Materials, BMC Bioinformatics, Journal of Imaging, Frontiers in Plant Science, Entropy, IJERPH) |
| Published papers, 2024 | 281 papers | same journals |
| Published papers, 2026 | 238 papers | same journals, May to November 2026 |
| Model-written sections | 404 sections | Claude Haiku 5.5 (342) and Sonnet 5.5 (62), three tasks on 2019 human sections: write from title and abstract, write from notes of the human text, polish the human text |
| Human vs model, six genres | 8,290 texts per source | HAP-E corpus (Reinhart et al. 2025): human text, GPT-4o, Llama 3 70B instruct and base |

About 150 style measures were computed per text (`scripts/stylo.py`): sentence and paragraph shape, punctuation, sentence openers, constructions, function words, and how many sentences contain something checkable.

## 2. Findings

**The register comes from post-training, not from language modelling.** In HAP-E academic text, GPT-4o differed from humans by more than one standard deviation on 24 of 153 measures and Llama 3 70B instruct on 13; the Llama 3 base model differed by that much on none. Largest gaps for GPT-4o (human median, model median): trailing `-ing` clauses 2.2 vs 13.2 per 1,000 words; sentence-length standard deviation 11.1 vs 6.2; numbers 39 vs 10; parentheses 25 vs 4; `is/are/was/were` 30 vs 15; passives 13 vs 4. A 2026 preprint reports the same from the detector side: base-model text was scored 97-99% human by GPTZero and Pangram, instruct-model text 17-30% (arXiv 2605.19516).

**The same structural gaps appear in every genre.** Across academic, news, blog, fiction, speech and scripts, both instruction-tuned models showed lower sentence-length variation (d = -1.2 to -2.9), more trailing `-ing` clauses, more nominalisations and longer words, fewer `is/was`, and fewer `so`, `because`, `then`, `very`.

**Published papers have moved.** Within the same journals, 2019 to 2026 (median per paper; rates per 1,000 words):

| Measure | 2019 | 2024 | 2026 |
|---|---|---|---|
| Mean word length (letters) | 5.33 | 5.57 | 6.00 |
| `of` | 39.6 | 35.5 | 27.3 |
| `is/are/was/were/be` | 39.3 | 32.7 | 31.3 |
| Nominalisations | 61.8 | 67.0 | 81.1 |
| Trailing `-ing` clauses | 1.6 | 4.1 | 4.5 |
| Evaluative words | 5.1 | 10.4 | 9.2 |
| `we` | 2.4 | 2.2 | 0.8 |
| Citations | 10.3 | 10.0 | 7.7 |

**Vocabulary tells rotate; structural ones stay.** Share of papers containing the phrase:

| Phrase | 2019 | 2024 | 2026 |
|---|---|---|---|
| `underscores` | 1% | 18% | 13% |
| `valuable insights` | 1% | 16% | 3% |
| `rather than` | 27% | 35% | 82% |
| `be interpreted as` | 4% | 2% | 36% |
| `across` | 34% | 69% | 90% |
| `in order to` | 62% | 41% | 21% |
| `there is` | 60% | 62% | 26% |
| `on the other hand` | 40% | 38% | 15% |

Graphite's September 2026 study of 90,000 model-written articles found the same: 55-72% of each model's tells were unique to that version, while sentence-length standard deviation stayed at 5.8-8.4 against 17.0 for humans. Wikipedia's "Signs of AI writing" lists a different word set for each model period.

**Late-2026 models have their own signature.** Haiku 5.5 and Sonnet 5.5 writing from notes used shorter sentences than the human originals, almost no sentence-initial `Moreover/Furthermore/Thus` (24%, 21% and 19% of human sections; 4%, 1% and 0% of the 135 model sections), and more `so`, `because`, `together, these`, `taken together`. Guidance written for 2024 models ("shorter sentences, fewer connectives, active voice") pushes a paper toward this signature.

**What a detector responds to.** Scores from an open academic detector (desklib/ai-text-detector-academic-v1.01), share of texts scored above 0.5:

| Texts | Flagged |
|---|---|
| 2019 papers (intro, methods, results, discussion; 70 each) | 23-31% |
| 2024 papers | 46-67% |
| 2026 papers | 60-83% |
| Haiku 5.5, polishing human text | 80% |
| Haiku 5.5, writing from notes | 92% |
| Haiku 5.5, writing from title and abstract | 100% |

Among the 193 model-written sections, the measures most correlated with the detector score (Spearman): share of sentences tied to a number, citation, name or parenthesis (-0.63); citations (-0.55); parentheses (-0.53); paragraphs ending on an unanchored sentence (+0.51); word variety (+0.49); punctuation variety (-0.43). Karr et al. (arXiv 2608.11256) report the matching result for Pangram and GPTZero: scores rise with academic-word and long-word density and fall with numeric and symbol tokens.

**Rewriting test.** Ten Haiku-written sections (from notes) and six sections of a model-drafted manuscript were rewritten by Sonnet 5.5 under each strategy. Median detector score:

| Strategy | Model-written sections (desklib / fakespot) | Manuscript sections (desklib) |
|---|---|---|
| Original | 0.88 / 0.75 | 0.25 |
| "Make it sound human" | 0.71 / 0.49 | 0.29 |
| Pattern-list humanizer | 0.76 / 0.41 | 0.20 |
| Human example passages as style reference | 0.88 / 0.80 | 0.30 |
| This skill's research-paper profile, no author input | 0.68 / 0.19 | 0.11 |
| Human 2019 papers, for scale | 0.22 / 0.27 | |

With 10 and 6 items these are indications, not estimates. No strategy brought model-written text to the human level on the stronger detector without new content from an author. That agrees with ARB (arXiv 2607.29539), where same-model rewrites of model text stayed 78-83% detected, and with Russell et al. (ACL 2025), where paraphrasing did not fool expert readers.

## 3. What follows for the design

1. Measure against human baselines for the specific kind of text, in both directions. A list of banned patterns goes stale and can overshoot.
2. Put the author's content first. Anchoring sentences to checkable detail is the largest lever found and the one that rewording cannot supply.
3. Rewrite from facts, not from the model's sentences.
4. Keep word lists as dated data with a tool to regenerate them.
5. Make no promise about detectors. They flagged a quarter of pre-LLM papers here, and 9-15% of recent human abstracts in Karr et al.

## 4. Limits

- Baselines are English, from 12 open-access journals. Fields differ, so a writer's own samples are the better reference.
- Model samples are from two Claude models; GPT-4o and Llama 3 data are from 2024. Gemini and GPT models of 2026 were covered only through published studies and the 2026 paper drift.
- The detectors used are open models. Commercial detectors (Pangram, GPTZero, Turnitin) were not tested and may behave differently.
- The genre baselines other than papers come from HAP-E 500-word chunks with no paragraph breaks, so paragraph measures are missing there.
- The 2024 and 2026 paper sets contain an unknown mix of human and model-assisted writing.

## 5. Sources

- Reinhart et al., "Do LLMs write like humans? Variation in grammatical and rhetorical styles", PNAS 122(8), 2025. https://arxiv.org/abs/2410.16107 (HAP-E corpus: https://huggingface.co/datasets/browndw/human-ai-parallel-corpus)
- Kobak et al., "Delving into LLM-assisted writing in biomedical publications through excess vocabulary", Science Advances 11(27), 2025. https://arxiv.org/abs/2406.07016
- Rallapalli et al., "Interpretable Stylistic Variation in Human and LLM Writing Across Genres, Models, and Decoding Strategies", 2026. https://arxiv.org/abs/2604.14111
- Zanotto and Aroyehun, "Human Variability vs. Machine Consistency", 2024. https://arxiv.org/abs/2412.03025
- Karr et al., "Why AI Detection Fails for Academic Integrity", 2026. https://arxiv.org/abs/2608.11256
- "Base Models Look Human To AI Detectors", 2026. https://arxiv.org/abs/2605.19516
- "ARB: A Matched Authorship-Rewriting Benchmark Dataset for AI-Text Detector Evaluation", 2026. https://arxiv.org/abs/2607.29539
- "Attacks on Machine-Text Detectors Retain Stylistic Fingerprints", 2025. https://arxiv.org/abs/2505.14608
- Russell, Karpinska and Iyyer, "People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text", ACL 2025. https://arxiv.org/abs/2501.15654
- Emi and Spero, "Technical Report on the Pangram AI-Generated Text Classifier", 2024. https://arxiv.org/abs/2402.14873
- Hamilton and Mimno, "Elias in the Lighthouse, Again? Diagnosing Low Diversity in LLM Stories", EMNLP 2026. https://arxiv.org/abs/2605.26492
- Geng, Dong and Poibeau, "Beyond Via: Analysis and Estimation of the Impact of Large Language Models in Academic Papers", 2026. https://arxiv.org/abs/2603.25638
- Utami and Sasano, "Can We Still Trace L1 Signals?", EMNLP 2026. https://arxiv.org/abs/2604.08568
- Graphite, "AI tells", September 2026. https://graphite.io/research/ai-tells
- Wikipedia, "Signs of AI writing" (WikiProject AI Cleanup). https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- Liang et al., "GPT detectors are biased against non-native English writers", 2023. https://arxiv.org/abs/2304.02819
