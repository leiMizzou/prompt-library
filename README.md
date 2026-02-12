# 📚 prompt-library

**Reusable prompt templates for AI agents and developers.**

Stop rewriting the same prompts. Store, search, and reuse them.

```
$ prompt-library list

📚 prompt-library v0.1.0 — 16 templates

  💻 coding
     code-review          Code Review
     bug-fix              Bug Fix Assistant
     write-tests          Write Unit Tests
     refactor             Refactor Code
     commit-message       Git Commit Message
     ...

  📝 summarization
     summarize            Summarize Text

  🌐 translation
     translate            Translate Text
```

## Install

```bash
pip install prompt-library
```

Or download:
```bash
curl -O https://raw.githubusercontent.com/leiMizzou/prompt-library/main/prompt_library.py
```

## Usage

```bash
# List all templates
prompt-library list

# View a template
prompt-library get code-review

# Use with variables
prompt-library use code-review --var code="def foo(): pass"
prompt-library use translate --var source_lang=English --var target_lang=French --var text="Hello"
prompt-library use commit-message --var diff="$(git diff --staged)"

# Search
prompt-library search "test"
prompt-library search "git"

# Add your own
prompt-library add my-prompt -n "My Prompt" -c coding -t "custom" --template "Do {{task}}"
echo "Analyze {{data}}" | prompt-library add analyzer -n "Analyzer" -c analysis

# Manage
prompt-library tags       # List all tags
prompt-library remove my-prompt
prompt-library export > my-prompts.json
prompt-library import shared-prompts.json
prompt-library reset      # Reset to built-in defaults
```

## Template Variables

Templates use `{{variable}}` syntax:

```
Review this code: {{code}}
Translate from {{source}} to {{target}}: {{text}}
```

Fill them with `--var key=value`:
```bash
prompt-library use translate --var source=English --var target=French --var text="Hello world"
```

## Built-in Templates (16)

| ID | Category | Description |
|----|----------|-------------|
| code-review | coding | Code review with severity levels |
| bug-fix | coding | Debug and fix errors |
| write-tests | coding | Generate unit tests |
| refactor | coding | Refactor for readability |
| explain-code | coding | Step-by-step code explanation |
| commit-message | coding | Conventional commit messages |
| pr-description | coding | Pull request descriptions |
| api-docs | coding | API endpoint documentation |
| regex-helper | coding | Build and explain regex patterns |
| summarize | summarization | Bullet-point summaries |
| translate | translation | Preserves tone and formatting |
| system-prompt | system | Build system prompts |
| agent-persona | agent | Design agent personalities |
| data-analysis | analysis | Dataset insights and recommendations |
| email-draft | writing | Professional email drafting |
| tech-explainer | writing | Explain concepts to any audience |

## License

MIT
