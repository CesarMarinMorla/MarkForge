---
title: "List Tests"
subtitle: "Bullet, ordered, and mixed list scenarios"
author: "MarkForge QA"
date: "June 2026"
toc: true
titlepage-rule-color: "4A8FE7"
---

## Bullet List

- Authenticate via LDAP against Active Directory
- Authorize using RBAC with four distinct roles
- Audit all access attempts with timestamps
- Alert on anomalous authentication patterns

## Ordered List

1. Plan the infrastructure requirements
2. Provision the virtual machines
3. Configure the network policies
4. Deploy the application stack
5. Validate the end-to-end pipeline
6. Document the architecture decisions

## Single Item Lists

- This is a bullet list with only one item.

1. This is an ordered list with only one item.

## Mixed Content in Section

This section contains a bullet list followed by body text and an ordered list.

- Frontend: React 19 with TypeScript
- Backend: Node.js with Express 5
- Database: PostgreSQL 16

The stack is containerized with Docker and orchestrated via Kubernetes. Each component has a health check endpoint monitored by the platform.

1. Verify all health endpoints return 200
2. Check memory usage below threshold
3. Confirm log output is error-free
4. Report summary to monitoring dashboard

## List With Empty Lines

- Item one

- Item two

- Item three

1. First step

2. Second step

3. Third step
