---
title: "Converter Features — Visual Check"
subtitle: "Open the PDF and verify each section looks correct"
author: "MarkForge QA"
date: "June 2026"
toc: true
titlepage-rule-color: "E94560"
---

## How To Use This Document

Each section below exercises one P1 markdown converter feature. When you open the generated PDF, you should **see** the layout described — not just find the words in a text search.

| Section | What you should see |
|---|---|
| Task Lists | Empty and checked box glyphs before each line |
| Nested Bullets | Second-level bullets indented to the right |
| Nested Ordered | Sub-steps numbered 1, 2 under their parent (not 3, 4) |
| Definition Lists | Bold terms with definitions indented below |
| Markdown Images | A large colored rectangle with a caption underneath |

## Task Lists

Each line below should show a checkbox glyph at the left margin.

- [ ] Unchecked: deploy to staging environment
- [x] Checked: run security scan on release branch
- [ ] Unchecked: update operator runbook

## Nested Bullets

The two middle items should appear indented relative to the outer bullets.

- OUTER — infrastructure layer
  - INNER load balancer pool
  - INNER database replica set
- OUTER — application layer

## Nested Ordered

Nested steps should restart at 1 under their parent item.

1. OUTER — provision cluster
2. OUTER — configure networking
   1. INNER assign pod CIDR
   2. INNER open firewall rules
3. OUTER — deploy workloads

## Definition Lists

Each term should render in bold; definitions should sit on the following lines, indented.

YAML frontmatter
: Key-value metadata at the top of a markdown file, delimited by `---`.

ReportLab Platypus
: High-level PDF layout API used by MarkForge for flowing document content.

## Markdown Images

A large accent-colored block should appear below — not alt text alone.

![Accent color fixture block — 160 by 80 points](fixture.png)

If the block above is missing, image path resolution or embedding failed.
