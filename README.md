## ✨ Weekly Status Update Generator

Automate the generation and emailing of your weekly status emails to your manager with a local Ollama AI model instance and the Obsidian vault markdown notes you already write.

```
============================================================
EMAIL PREVIEW
============================================================
From: janine.s.huang@jpl.nasa.gov
To: <your_manager>@jpl.nasa.gov
Cc: janine.s.huang@jpl.nasa.gov
Subject: Janine Huang Week 34 Status
------------------------------------------------------------
Here is your weekly status report:

**DOM:**
* Successfully finalized closeout of DM project.

**MRO:**
* Presented Downlink Data presentation at Project Science Group Conference, achieving success.
* Addressed Brian Kahovec's question about MSL relay pass.
* Recovered partial retransmit data on Saturday and Sunday, with 77% recovery rate.

**M20 OCS:**
* Successfully uploaded new ZIP files to GitHub repository.
* Updated deployment config file and modified ID in the config file.
* Ran Python tests and identified most failures, currently working to resolve issues.

**DM:**
* Quit DM project to reduce mental overload on other projects, with plans to finalize closeout.

**Other Projects and Activities:**
* No significant accomplishments.

---
This status update was generated and submitted by XJ9, Janine's bot, 
using her personal notes and may contain inaccuracies. Please verify any critical 
information directly with her if needed.

Best,
XJ9
```

This tool is based off of Janine's Obsidian file tree setup:

```
Obsidian Vault/
  |-- 0. Q4 2024/
    ├── 2024 - WK 41.md 
    ├── 2024 - WK 40.md 
    ├── 2024 - WK 39.md 
    └── etc...
```

Where each week markdown file has the same general format:
```
# Project 1
[notes]
# Project 2
[notes]
# Project ...
[notes]
# Project n
[notes]
```

### How it works
1. Finds the target folder based off a prefix. 
    - I have mine set to `0. `, which in Obsidian, default sorts this folder to the top of the file navigator.
    - I'll create a new one every Q# and archive older Q#s in an `/archive` folder in my Obsidian Vault.
2. Detects last week's markdown notes based off the suffix `*<iso_week_number>.md`.
    - The week # can be overwritten to generate a report for a specific week
3. Uses the Llama3 LLM to extract important information and generate a concise report.
4. Optionally sends an email to your manager if you approve the report. 
    - If not approved, you can suggest an edit to the LLM to regenerate a better response before sending.

### Requirements
  - Python 3.x
  - Ollama

### Installation and Usage
1. Clone and change into project directory
```bash
git clone <repository-url>
cd <repository-directory>
```
2. Update the configuration constants in `config.py`
3. Setup JPL LDAP email credentials to save to your shell profile
```bash
python setup_email.py
```

### Usage

```bash
# Generate status for previous week only (no email)
python weekly_status.py

# Generate status for specific week and send email to specific recipient
python weekly_status.py --week 42 --email recipient@jpl.nasa.gov
```

**Optional Arguments:**
- `-h` or `--help`: View help message
- `--week <week_number>`: Specify ISO week number (defaults to previous week if not provided)
- `--email <recipient>`: Send email (uses default recipient in config if no email address provided)


### Additional Notes
- Markdown files must be organized within the specified directory (`OBSIDIAN_DIR`).
- The `ACTIVE_PROJECTS` constant should match your projects as you reference them in your Obsidian notes.
- Email functionality requires the `EMAIL_PASSWORD` environment variable to be set.
- Obsidian is technically not a requirement, and can be used with just pure markdown files.
