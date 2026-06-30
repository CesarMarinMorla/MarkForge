---
title: "MarkForge Test Suite"
subtitle: "Comprehensive Feature Coverage for PDF Generation"
author: "MarkForge QA Team"
date: "June 2026"
toc: true
index: true
titlepage-rule-color: "0D3B66"
---

> This document tests every feature of the <<MarkForge>> PDF engine. All content is synthetic and contains no personal or private information.

## 1. Text Formatting

This section covers **bold text**, *italic text*, and ***bold italic*** combinations. Inline `code` spans are rendered in a monospace font (Menlo on macOS, Courier fallback) with a rounded light gray background.  Applications using <<ReportLab>> include this PDF engine.

Links are rendered with an accent color underline: [MarkForge Engine](https://example.com/markforge) and [ReportLab](https://www.reportlab.com/).

Accented characters: á é í ó ú ñ ü Á É Í Ó Ú Ñ. Unicode symbols: © ® ™ ¶ • § ∞ ≈ ≠ ≤ ≥ ± ← ↑ → ↓ ↔ ↕ ⇒ ⇔ ∑ ∫ √ π.

### 1.1 Sub-heading level 3

This text appears under a sub-heading rendered as bold in the body.

#### 1.1.1 Sub-heading level 4

Deeper nesting works too. The engine handles `###`, `####`, `#####`, and `######` uniformly as bold body text.

----

## 2. Tabular Data

Pipe tables with various column counts and content types are rendered via <<ReportLab>> table components.

### 2.1 Equipment Inventory

| ID | Name | Status | Location |
|---|---|---|---|
| 001 | Alpha Server | active | Rack A-12 |
| 002 | Beta Workstation | maintenance | Lab 3 |
| 003 | Gamma Router | active | NOC |
| 004 | Delta Switch | retired | Storage |

### 2.2 Empty Cells

| Product | Price | Stock | Notes |
|---|---|---|---|
| Widget A | 12.50 | 143 | |
| Widget B | 8.00 | | Out of stock |
| Widget C | | 22 | Discontinued |
| Widget D | 25.00 | 7 | |

### 2.3 Single Row

| Key | Value |
|---|---|
| Version | 2.4.1 |

----

## 3. Code Blocks

Fenced code blocks with and without language identifiers.

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"


items = ["alpha", "beta", "gamma"]
for item in items:
    print(hello(item))
```

```javascript
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
console.log(fibonacci(10));
```

### 3.1 Unicode in Code

Box-drawing characters used in terminal output:

```
┌──────────┬──────────┬──────────┐
│ Server   │  Status  │  Uptime  │
├──────────┼──────────┼──────────┤
│ node-01  │  online  │  142d    │
│ node-02  │  online  │   89d    │
│ node-03  │  offline │    0d    │
└──────────┴──────────┴──────────┘
```

Arrows and math symbols in comments:

```python
# Pipeline stages: input → process → output
# Threshold: max >= min ± tolerance
# Condition: status ≈ expected ≈ actual
result = data >> transform(x) >> validate()  # type: ignore
```

### 3.2 No Language Tag

```
This is a plain code block without a language identifier.
It should render with the same monospace font and gray background.
Indentation is preserved.
    Four spaces
        Eight spaces
```

----

## 4. Lists

### 4.1 Bullet List

- Authenticate via LDAP against Active Directory
- Authorize using RBAC with four distinct roles
- Audit all access attempts with timestamps
- Alert on anomalous authentication patterns

### 4.2 Ordered List

1. Plan the infrastructure requirements
2. Provision the virtual machines
3. Configure the network policies
4. Deploy the application stack
5. Validate the end-to-end pipeline

### 4.3 Mixed Content

Section with a bullet list followed by body text and a table:

- Frontend: React 19 with TypeScript
- Backend: Node.js with Express 5
- Database: PostgreSQL 16

The stack is containerized with Docker and orchestrated via Kubernetes. Each component has a health check endpoint monitored by the platform.

| Component | Port | Protocol |
|---|---|---|
| API Gateway | 443 | HTTPS |
| Web App | 3000 | HTTP |
| Database | 5432 | TCP |

----

## 5. Callouts and Highlights

Blockquotes render as highlighted call-out boxes with a colored left border.

> This is a standard blockquote rendered as a highlight box. It appears with a bold font and accent color, drawing attention to important information.

> Security notice: All credentials must be stored in environment variables, never in code. The system will refuse to start if required secrets are missing.

Multiple blockquotes: the engine uses only the first one per section and renders it as a highlight call-out.

----

## 6. Complex Section

This section combines multiple element types to verify correct layout stacking.

### 6.1 Architecture Overview

The system follows a layered architecture with strict dependency rules. Each layer communicates exclusively with the layer directly below it.

```
┌──────────────────────────────────────────┐
│            Presentation Layer            │
│         (React SPA + Tailwind)           │
├──────────────────────────────────────────┤
│            Application Layer             │
│       (Express Controllers + Auth)       │
├──────────────────────────────────────────┤
│               Domain Layer               │
│         (Services + Business Logic)      │
├──────────────────────────────────────────┤
│           Persistence Layer              │
│    (Repositories + Data Access Objects)  │
└──────────────────────────────────────────┘
```

### 6.2 Deployment Topology

| Node | Role | Specs |
|---|---|---|
| master-01 | Control plane | 4 vCPU, 8 GB RAM |
| node-01 | Worker | 8 vCPU, 16 GB RAM |
| node-02 | Worker | 8 vCPU, 16 GB RAM |
| node-03 | Worker (spot) | 4 vCPU, 8 GB RAM |

Deployment steps:

1. Provision nodes via Terraform
2. Install Kubernetes with kubeadm
3. Deploy CNI plugin (Calico)
4. Install ingress controller
5. Deploy application manifests
6. Configure monitoring stack

Key metrics to observe:

- CPU utilization should stay below 80%
- Memory usage must not trigger OOM killer
- Network latency under 10ms between nodes
- Disk IPS within provisioned limits

> The spot instance (node-03) should not run stateful workloads. Use pod anti-affinity to prefer scheduling on persistent nodes.

----

## 7. Edge Cases

### 7.1 Very Long Text Without Breaks

Supercalifragilisticexpialidocious antidisestablishmentism floccinaucinihilipilification pneumonoultramicroscopicsilicovolcanoconiosis. These lengthy terms test text wrapping behavior in justified paragraphs across multiple lines without causing overflow or truncation in the PDF output.

### 7.2 Single Character Cell

| A | B | C |
|---|---|---|
| x | y | z |
| 1 | 2 | 3 |

### 7.3 Numeric and Special Characters

| Symbol | Code | Description |
|---|---|---|
| Non-breaking space | &nbsp; | HTML entity preserved in source |
| Less than | &lt; | XML entity |
| Greater than | &gt; | XML entity |
| Ampersand | &amp; | XML entity |
| Line separator | \u2028 | Unicode separator |

----

## 8. Extensive Table

| Feature | Status | Version | Priority | Notes |
|---|---|---|---|---|
| Cover page | done | 1.0.0 | high | Themed with accent bar |
| Table of contents | done | 1.0.0 | high | MultiBuild two-pass |
| Custom fonts | done | 1.1.0 | high | TTF registration |
| Header/footer config | done | 1.1.0 | medium | Placeholder system |
| Schema validation | done | 1.1.0 | high | Full error reporting |
| System font detection | done | 1.2.0 | medium | Menlo auto-detect on macOS |
| Inline code formatting | done | 1.2.0 | medium | Monospace inline style |
| Section numbering | pending | 2.0.0 | low | Auto-generated |
| Image alignment | pending | 2.0.0 | low | Left/center/right |
| SVG support | pending | 2.0.0 | low | Vector graphics |

----

## 9. Final Section

This is the last section. It verifies that the TOC entry count, page numbering, and overall document structure are correct when the engine processes multiple sections with varying content types.

The document should include:

- A cover page with title, subtitle, and metadata table
- A table of contents listing all nine sections
- Body text with justified alignment throughout
- Proper header and footer on every page
- Consistent font rendering across all elements

*End of test document.*
