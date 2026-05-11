---
name: export-html-report
description: Generate a self-contained, presentation-ready HTML report from any completed analysis or conversation output. Use after finishing an investigation, security scan, query analysis, or incident analysis when the engineer wants to share findings with a customer or stakeholder as a polished document. 
keywords: html report, export, share, presentation, summary report, client report, generate html
version: "1.0.0"
---

# Export HTML Report

Generate a self-contained, presentation-ready HTML file that summarises the analysis or findings from the current conversation. The output must be visually clean, well-structured, and suitable for sharing with customers or stakeholders without further editing.

## When to Use

Invoke this skill when:
- The engineer asks to "generate a report", "export to HTML", "create a summary", "make this presentable", or similar

## Required Inputs (read from conversation context)

All inputs are derived from the current conversation — do **not** ask the user for content that is already present:

| Input | Source |
|---|---|
| Product and update level | Intake |
| Analysis type | Incident / Query / Security Scan / General |
| Key findings | The analysis already produced in this session |
| Recommendations / next steps | The analysis already produced in this session |
| Root cause and workaround (if incident) | Incident analysis output |

## Output File

- **Filename:** `report.html` (or a more descriptive name if the issue type warrants it, e.g. `security-report.html`, `incident-report.html`)
- **Format:** Single self-contained HTML file — all CSS inlined in a `<style>` block, no external dependencies, no JavaScript required for reading

## HTML Design Guidelines

### Overall Aesthetic
- Clean, professional, corporate look — suitable for a customer-facing document
- Colour palette: dark navy header (`#0d1b2a` / `#1b3a5c`), white content cards, light grey background (`#f4f6f9`), blue accent (`#2e86de`)

### Required Structural Elements

1. **Header bar** — dark navy background, contains:
   - Report title (e.g. "Impact Assessment Report", "Incident Analysis Report", "Query Analysis Report")
   - Metadata chips: Issue ID, Product, Update Level, Date, Issue Type

2. **Overall Verdict / Summary banner** — coloured left-border card (green for low/resolved, amber for medium/in-progress, red for high/critical):
   - Icon + bold verdict heading + one-sentence explanation
   - Border colour:
     - Green (`#27ae60`): Low risk / Resolved / No action required
     - Amber (`#f39c12`): Medium risk / Action recommended
     - Red (`#e74c3c`): High / Critical / Immediate action required

3. **Section headings**

4. **Content cards**

5. **Tables**

6. **Code blocks** — `<code>` inline snippets with monospace font and light grey background; for multi-line config use `<pre><code>` with slightly darker background and padding

## Step-by-Step Generation Process

1. **Read the conversation** — identify the analysis type, issue metadata, and all key findings already produced
2. **Determine the output path**
3. **Draft the section list** — map findings to the appropriate sections for this analysis type
4. **Write the HTML file** using the Write tool — single file, all CSS in `<style>`, no external links
5. **Confirm to the engineer** — state the full file path