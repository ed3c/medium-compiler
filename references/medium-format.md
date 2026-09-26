# Medium format reference

Checked 2026-09-26 against Medium's public documentation.

## Official sources

- Story editor: https://help.medium.com/hc/en-us/articles/215194537-Using-the-story-editor
  - documents headings/subheadings, links, quote blocks, lists, images/embeds/code and inline code;
  - does not expose a native table block.
- Embeds: https://help.medium.com/hc/en-us/articles/214981378-Using-embeds
  - third-party content can be embedded; this does not make tables a native editor block.
- Automatic table of contents:
  https://medium.com/blog/long-reads-on-medium-just-got-easier-to-read-and-enjoy-2a9f8fa135f8
  - Medium web automatically builds TOC from headings and subheadings.

## Final-body policy

1. no Markdown table;
2. no HTML table;
3. comparison matrices become labeled blocks, lists, or Option A / Option B;
4. fixed-width runtime/data-flow may use fenced text blocks;
5. headings are the navigation surface; do not duplicate a manual TOC unless requested.
