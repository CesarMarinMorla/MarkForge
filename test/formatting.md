---
title: "Inline Formatting Tests"
subtitle: "Bold, italic, links, code, and special characters"
author: "MarkForge QA"
date: "June 2026"
toc: true
titlepage-rule-color: "A23B72"
---

## Bold and Italic

**Bold text** using double asterisks. *Italic text* using single asterisks. __Bold with underscores__ and _italic with underscores_.

***Bold italic with asterisks*** and ___bold italic with underscores___.

## Links

[Simple link](https://example.com) with no special chars. [Link with path](https://example.com/page?id=123&lang=en) containing query parameters.

## Inline Code

Use `git status` to check repository state. Run `npm install && npm run build` to compile. The `process.env.NODE_ENV` variable controls the environment.

## Mixed Formatting

This paragraph has **bold**, *italic*, `code`, and a [link](https://example.com) all in one sentence. Also ***bold italic*** for good measure.

## Edge Cases

**bold with _italic_ inside** should render correctly. So should *italic with **bold** inside*.

Empty formatting: **** should not break the renderer. Same goes for ******.
