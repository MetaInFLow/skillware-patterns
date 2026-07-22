---
name: unrelated-investment-skill-directory
description: List unrelated investment tools. Use only to demonstrate a directory and workflow with incompatible result shapes.
intent: Show a Composite near miss whose market, financial, and risk steps cannot be treated through one Component contract.
type: workflow
---

# Unrelated Investment Skill Directory

Run these tools in any convenient order:

- market notes return a Markdown bullet list;
- financial analysis returns `{revenue, burn, runway}`;
- competition analysis writes an unstructured document;
- risk analysis returns `{severity, mitigations}`.

The root returns only paths to those outputs. It does not require a shared
result contract, does not return child section records, and does not validate
part-whole references or cycles. Its workflow also lets two groups reuse the
same risk output, producing a shared-child DAG instead of a tree.
