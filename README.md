<p align="center">
  <img src="assets/logo.png" alt="Kairos Logo" width="220">
</p>

<h1 align="center">Kairos</h1>

<p align="center">
  <strong>Privacy-first AI time reporting powered by a local LLM.</strong>
</p>

<p align="center">
  Automatically track your workday, group related activities into meaningful work sessions,
  and generate professional consultant time reports using <strong>Ollama</strong> — without sending your activity data to the cloud.
</p>

---

##  Features

-  Privacy-first – all AI processing runs locally with Ollama
-  Automatic activity tracking
-  Groups raw activity into meaningful work sessions
-  Generates professional consultant time reports
-  Git integration for additional development context
-  Unit tested and fully formatted with Ruff + Black

---

##  Why Kairos?

Writing accurate time reports is repetitive and easy to forget.

Kairos continuously records your work activity, understands what you worked on, and produces a clean, professional summary that you can review before submitting.

Kairos is designed to **assist**, not monitor.

It keeps you in control while removing the repetitive work of writing time reports.

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/Thomashallberg/Kairos.git
cd Kairos
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Install

```bash
pip install -e .
```

---

##  Requirements

- Python 3.14+
- Ollama
- Windows (current activity tracker)
- A local Ollama model

Example:

```bash
ollama serve
ollama pull llama3.1
```

---

##  Usage

Start tracking

```bash
kairos track
```

View raw tracked activity

```bash
kairos report today
```

Generate an AI time report

```bash
kairos summarize today
```

Summarize another date

```bash
kairos summarize 2026-08-01
```

---

##  Example

Raw activity

```text
09:30–10:20 | Development | Code.exe | activity_service.py
10:20–10:45 | Issue Tracking | Chrome | Jira
10:45–12:00 | Development | Code.exe | prompt_builder.py
```

↓

AI-generated report

```text
09:30–10:20: Development work on activity service.

10:20–10:45: Investigated issue KAI-123 in Jira.

10:45–12:00: Developed prompt generation for consultant time reporting.
```

---

##  Architecture

```text
Activity
    │
    ▼
Activity Grouper
    │
    ▼
Work Block
    │
    ▼
Work Session
    │
    ▼
Report Period
    │
    ▼
Prompt Builder
    │
    ▼
Ollama
    │
    ▼
Professional Time Report
```

---



###  Version 1.0

- Activity tracking
- Work session detection
- Report period grouping
- Git integration
- Local AI summaries
- CLI

###  Version 1.1

- Smarter grouping of supporting activities
- Configurable activity rules
- Export to PDF
- Export to Excel
- Better consultant report templates

---



##  Author

Thomas Hallberg

Built as a portfolio project demonstrating Python, clean architecture, local AI integration, testing, and software design.