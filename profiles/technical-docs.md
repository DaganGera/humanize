# Profile: technical documentation, README

No built-in baseline. A project's existing human-written docs are the reference: `H baseline docs/*.md -o voice.json`. `H measure` skips code blocks, tables and inline code.

## What human docs look like

Uneven. Terse where the reader knows the ground, detailed at the one step that goes wrong. Commands, versions, paths and error messages are quoted exactly. Reasons appear where a choice is surprising. Second person or imperative.

## How model-written docs differ

Every section gets the same weight and the same shape. A feature list of bold labels with a restating sentence each. Adjectives where a fact belongs ("fast", "robust", "seamless", "powerful"). An overview that says what the document will cover, and a conclusion. Explanations of what was changed from an earlier version instead of what is true now. Emoji headings.

## Rewriting

1. Lead with what the thing does and the command to run it.
2. Replace each adjective with the fact behind it (the timing, the limit, the supported versions) or delete it.
3. Give the failure case: what breaks, the exact error, the fix. Ask the maintainer for these; they are what the model did not know.
4. Describe current behaviour. History goes in the changelog.
5. Cut the overview of the document and the closing summary. Cut sections that have nothing in them.
6. Sentence-case headings, no decorative emoji, bold only for the term being defined or a warning.

Never alter code, commands, paths, config keys, version numbers or output.
