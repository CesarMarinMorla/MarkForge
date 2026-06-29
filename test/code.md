---
title: "Code Block Tests"
subtitle: "Fenced code blocks with language tags, Unicode, and multiple blocks"
author: "MarkForge QA"
date: "June 2026"
toc: true
titlepage-rule-color: "E09F3E"
---

## Python

```python
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
```

## JavaScript

```javascript
async function fetchData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
}
```

## No Language Tag

```
This is a plain code block without a language identifier.
It should render with the default monospace font and gray background.
Indentation is preserved.
    Four spaces
        Eight spaces
            Twelve spaces
```

## Unicode in Code

Box-drawing characters for terminal UI:

```
┌──────────┬──────────┬──────────┬──────────┐
│ Service  │  Status  │  Uptime  │  Port    │
├──────────┼──────────┼──────────┼──────────┤
│ web      │  online  │  142d    │  443     │
│ api      │  online  │   89d    │  8080    │
│ db       │  online  │  365d    │  5432    │
│ cache    │  offline │    0d    │  6379    │
└──────────┴──────────┴──────────┴──────────┘
```

Arrows and math symbols in comments:

```python
# Pipeline: input → transform → validate → output
# Threshold: max_value >= min_value ± tolerance
# Condition: result ≈ expected_value ≠ invalid
result = data >> processor(x) >> validator()  # type: ignore
```

## Multiple Blocks Per Section

First block:

```bash
docker build -t myapp:latest .
docker push registry.example.com/myapp:latest
```

Second block:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/myapp
```

Third block (no language):

```
This demonstrates that multiple code blocks in one section
are joined with double newlines preserving separation.
```
