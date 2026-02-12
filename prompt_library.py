#!/usr/bin/env python3
"""
📚 prompt-library — Reusable Prompt Templates for AI Agents.

Store, search, tag, and use prompt templates from a local library.
Ship with 15+ built-in templates for common AI tasks.

Usage:
    python prompt_library.py list
    python prompt_library.py get code-review
    python prompt_library.py use code-review --var code="def foo(): pass"
    python prompt_library.py search "test"
    python prompt_library.py add my-prompt --category coding --tags "python,review"
    python prompt_library.py tags

Zero dependencies. Python 3.8+.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

__version__ = "0.1.0"

LIBRARY_DIR = Path.home() / ".prompt-library"
LIBRARY_FILE = LIBRARY_DIR / "prompts.json"

# ─── Built-in Templates ─────────────────────────────────────────────────────

BUILTIN_PROMPTS = [
    {
        "id": "code-review",
        "name": "Code Review",
        "category": "coding",
        "tags": ["review", "quality", "best-practices"],
        "template": "Review this code for bugs, security issues, performance problems, and style.\nProvide specific suggestions with line references.\n\n```\n{{code}}\n```\n\nFormat: list each issue with severity (critical/warning/info), line number, and fix.",
    },
    {
        "id": "bug-fix",
        "name": "Bug Fix Assistant",
        "category": "coding",
        "tags": ["debug", "fix", "error"],
        "template": "I have a bug in my code.\n\nCode:\n```\n{{code}}\n```\n\nError message:\n```\n{{error}}\n```\n\nExplain the root cause and provide a corrected version.",
    },
    {
        "id": "write-tests",
        "name": "Write Unit Tests",
        "category": "coding",
        "tags": ["testing", "unittest", "pytest"],
        "template": "Write comprehensive unit tests for this code using {{framework}}.\nCover edge cases, error handling, and typical usage.\n\n```\n{{code}}\n```\n\nInclude at least 5 test cases with descriptive names.",
    },
    {
        "id": "refactor",
        "name": "Refactor Code",
        "category": "coding",
        "tags": ["clean-code", "refactor", "improve"],
        "template": "Refactor this code for better readability, maintainability, and performance.\nKeep the same behavior. Explain each change.\n\n```{{language}}\n{{code}}\n```",
    },
    {
        "id": "explain-code",
        "name": "Explain Code",
        "category": "coding",
        "tags": ["explain", "learn", "understand"],
        "template": "Explain this code step by step. Assume the reader is a {{level}} developer.\n\n```{{language}}\n{{code}}\n```\n\nCover: what it does, how it works, key concepts, and potential improvements.",
    },
    {
        "id": "summarize",
        "name": "Summarize Text",
        "category": "summarization",
        "tags": ["summary", "tldr", "condense"],
        "template": "Summarize the following text in {{length}}.\nPreserve key facts, numbers, and conclusions.\n\n---\n{{text}}\n---\n\nFormat: bullet points with the most important information first.",
    },
    {
        "id": "translate",
        "name": "Translate Text",
        "category": "translation",
        "tags": ["translate", "language", "i18n"],
        "template": "Translate the following from {{source_lang}} to {{target_lang}}.\nPreserve tone, formatting, and technical terms.\n\n---\n{{text}}\n---",
    },
    {
        "id": "system-prompt",
        "name": "System Prompt Builder",
        "category": "system",
        "tags": ["system", "persona", "instructions"],
        "template": "Create a system prompt for an AI assistant with these characteristics:\n- Role: {{role}}\n- Tone: {{tone}}\n- Key behaviors: {{behaviors}}\n- Constraints: {{constraints}}\n\nThe system prompt should be clear, specific, and under 500 words.",
    },
    {
        "id": "agent-persona",
        "name": "Agent Persona Designer",
        "category": "agent",
        "tags": ["agent", "persona", "character"],
        "template": "Design a detailed persona for an AI agent:\n- Name: {{name}}\n- Purpose: {{purpose}}\n- Target users: {{users}}\n\nInclude: personality traits, communication style, knowledge domains, limitations, example interactions.",
    },
    {
        "id": "data-analysis",
        "name": "Data Analysis Prompt",
        "category": "analysis",
        "tags": ["data", "analysis", "insights"],
        "template": "Analyze this dataset and provide insights:\n\n```\n{{data}}\n```\n\nInclude:\n1. Key patterns and trends\n2. Statistical summary\n3. Anomalies or outliers\n4. Actionable recommendations\n5. Suggested visualizations",
    },
    {
        "id": "email-draft",
        "name": "Email Draft",
        "category": "writing",
        "tags": ["email", "professional", "communication"],
        "template": "Draft a {{tone}} email:\n- To: {{recipient}}\n- Subject: {{subject}}\n- Key points: {{points}}\n- Call to action: {{cta}}\n\nKeep it concise and professional. Under 200 words.",
    },
    {
        "id": "commit-message",
        "name": "Git Commit Message",
        "category": "coding",
        "tags": ["git", "commit", "conventional"],
        "template": "Write a conventional commit message for this diff:\n\n```diff\n{{diff}}\n```\n\nFormat: type(scope): description\n\nTypes: feat, fix, docs, style, refactor, test, chore\nInclude body if changes are complex.",
    },
    {
        "id": "pr-description",
        "name": "PR Description",
        "category": "coding",
        "tags": ["git", "pull-request", "documentation"],
        "template": "Write a pull request description for these changes:\n\n{{changes}}\n\nInclude:\n- Summary (1-2 sentences)\n- What changed and why\n- How to test\n- Screenshots/examples if relevant\n- Breaking changes",
    },
    {
        "id": "api-docs",
        "name": "API Documentation",
        "category": "coding",
        "tags": ["api", "documentation", "openapi"],
        "template": "Generate API documentation for this endpoint:\n\n```\n{{code}}\n```\n\nInclude:\n- Endpoint URL and method\n- Request parameters (path, query, body) with types\n- Response format with example\n- Error codes\n- Usage example with curl",
    },
    {
        "id": "regex-helper",
        "name": "Regex Helper",
        "category": "coding",
        "tags": ["regex", "pattern", "validation"],
        "template": "Create a regex pattern that matches: {{description}}\n\nProvide:\n1. The regex pattern\n2. Explanation of each part\n3. Test cases (3 matching, 3 non-matching)\n4. Common edge cases\n5. Usage example in {{language}}",
    },
    {
        "id": "tech-explainer",
        "name": "Technical Concept Explainer",
        "category": "writing",
        "tags": ["explain", "technical", "education"],
        "template": "Explain {{concept}} to a {{audience}}.\n\nUse:\n- Simple analogy first\n- Then technical details\n- A practical example\n- Common misconceptions\n- Further reading suggestions",
    },
]

# ─── Library Management ──────────────────────────────────────────────────────

def load_library() -> List[Dict]:
    """Load prompts from library file, merging with built-ins."""
    if LIBRARY_FILE.exists():
        try:
            data = json.loads(LIBRARY_FILE.read_text())
            return data if isinstance(data, list) else []
        except:
            return list(BUILTIN_PROMPTS)
    return list(BUILTIN_PROMPTS)

def save_library(prompts: List[Dict]):
    """Save prompts to library file."""
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_FILE.write_text(json.dumps(prompts, indent=2))

def ensure_library():
    """Initialize library with built-ins if it doesn't exist."""
    if not LIBRARY_FILE.exists():
        save_library(BUILTIN_PROMPTS)

def get_prompt(prompts: List[Dict], prompt_id: str) -> Optional[Dict]:
    """Get a prompt by ID."""
    for p in prompts:
        if p["id"] == prompt_id:
            return p
    return None

def render_template(template: str, variables: Dict[str, str]) -> str:
    """Replace {{variable}} placeholders with values."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    
    # Find unreplaced variables
    missing = re.findall(r'\{\{(\w+)\}\}', result)
    return result, missing

# ─── Output ──────────────────────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

CATEGORY_ICONS = {
    "coding": "💻", "writing": "✍️", "analysis": "📊",
    "translation": "🌐", "summarization": "📝", "extraction": "🔍",
    "agent": "🤖", "system": "⚙️",
}

def format_prompt_list(prompts: List[Dict]) -> str:
    lines = []
    lines.append(f"\n{BOLD}📚 prompt-library v{__version__}{RESET}")
    lines.append(f"{DIM}{'─' * 65}{RESET}")
    lines.append(f"  {len(prompts)} templates available\n")
    
    by_cat = {}
    for p in prompts:
        cat = p.get("category", "other")
        by_cat.setdefault(cat, []).append(p)
    
    for cat in sorted(by_cat):
        icon = CATEGORY_ICONS.get(cat, "📄")
        lines.append(f"  {icon} {BOLD}{cat}{RESET}")
        for p in by_cat[cat]:
            tags = ", ".join(p.get("tags", [])[:3])
            lines.append(f"     {CYAN}{p['id']:<20}{RESET} {p['name']:<25} {DIM}{tags}{RESET}")
        lines.append("")
    
    lines.append(f"  {DIM}Use: prompt-library get <id> | prompt-library use <id> --var key=value{RESET}\n")
    return '\n'.join(lines)

def format_prompt_detail(p: Dict) -> str:
    lines = []
    icon = CATEGORY_ICONS.get(p.get("category", ""), "📄")
    lines.append(f"\n{icon} {BOLD}{p['name']}{RESET} ({CYAN}{p['id']}{RESET})")
    lines.append(f"  Category: {p.get('category', 'other')}")
    lines.append(f"  Tags: {', '.join(p.get('tags', []))}")
    
    # Find variables
    variables = re.findall(r'\{\{(\w+)\}\}', p.get("template", ""))
    if variables:
        lines.append(f"  Variables: {YELLOW}{', '.join(set(variables))}{RESET}")
    
    lines.append(f"\n{DIM}{'─' * 50}{RESET}")
    lines.append(p.get("template", ""))
    lines.append(f"{DIM}{'─' * 50}{RESET}\n")
    return '\n'.join(lines)

# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_vars(var_list: List[str]) -> Dict[str, str]:
    """Parse --var key=value pairs."""
    result = {}
    for v in (var_list or []):
        if '=' in v:
            key, value = v.split('=', 1)
            result[key.strip()] = value.strip()
    return result

def main():
    parser = argparse.ArgumentParser(prog="prompt-library", description="📚 Reusable prompt templates")
    sub = parser.add_subparsers(dest="command")
    
    sub.add_parser("list", help="List all prompts")
    
    get_p = sub.add_parser("get", help="Show a prompt template")
    get_p.add_argument("id", help="Prompt ID")
    
    use_p = sub.add_parser("use", help="Render a prompt with variables")
    use_p.add_argument("id", help="Prompt ID")
    use_p.add_argument("--var", "-v", action="append", help="Variable: key=value")
    
    search_p = sub.add_parser("search", help="Search prompts")
    search_p.add_argument("query", help="Search query")
    
    add_p = sub.add_parser("add", help="Add a new prompt")
    add_p.add_argument("id", help="Prompt ID (slug)")
    add_p.add_argument("--name", "-n", required=True, help="Display name")
    add_p.add_argument("--category", "-c", default="other")
    add_p.add_argument("--tags", "-t", default="", help="Comma-separated tags")
    add_p.add_argument("--template", help="Template text (or pipe via stdin)")
    
    rm_p = sub.add_parser("remove", help="Remove a prompt")
    rm_p.add_argument("id")
    
    sub.add_parser("tags", help="List all tags")
    
    exp_p = sub.add_parser("export", help="Export library")
    exp_p.add_argument("--file", "-f", help="Output file (default: stdout)")
    
    imp_p = sub.add_parser("import", help="Import prompts")
    imp_p.add_argument("file", help="JSON file to import")
    
    sub.add_parser("reset", help="Reset library to built-in defaults")
    
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--version", action="version", version=f"prompt-library {__version__}")
    
    args = parser.parse_args()
    ensure_library()
    prompts = load_library()
    
    if args.command == "list":
        if hasattr(args, 'json') and args.json:
            print(json.dumps([{"id": p["id"], "name": p["name"], "category": p.get("category")} for p in prompts], indent=2))
        else:
            print(format_prompt_list(prompts))
    
    elif args.command == "get":
        p = get_prompt(prompts, args.id)
        if not p:
            print(f"Prompt '{args.id}' not found.", file=sys.stderr)
            sys.exit(1)
        if hasattr(args, 'json') and args.json:
            print(json.dumps(p, indent=2))
        else:
            print(format_prompt_detail(p))
    
    elif args.command == "use":
        p = get_prompt(prompts, args.id)
        if not p:
            print(f"Prompt '{args.id}' not found.", file=sys.stderr)
            sys.exit(1)
        variables = parse_vars(args.var)
        rendered, missing = render_template(p["template"], variables)
        if missing:
            print(f"{YELLOW}Warning: unset variables: {', '.join(missing)}{RESET}", file=sys.stderr)
        print(rendered)
    
    elif args.command == "search":
        q = args.query.lower()
        matches = [p for p in prompts if 
                   q in p["id"].lower() or 
                   q in p.get("name", "").lower() or
                   q in p.get("template", "").lower() or
                   any(q in t.lower() for t in p.get("tags", []))]
        if matches:
            print(format_prompt_list(matches))
        else:
            print(f"No prompts matching '{args.query}'")
    
    elif args.command == "add":
        template = args.template
        if not template and not sys.stdin.isatty():
            template = sys.stdin.read()
        if not template:
            print("Provide template via --template or stdin", file=sys.stderr)
            sys.exit(1)
        
        new_prompt = {
            "id": args.id,
            "name": args.name,
            "category": args.category,
            "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
            "template": template,
        }
        prompts = [p for p in prompts if p["id"] != args.id]
        prompts.append(new_prompt)
        save_library(prompts)
        print(f"{GREEN}✓ Added '{args.id}'{RESET}")
    
    elif args.command == "remove":
        before = len(prompts)
        prompts = [p for p in prompts if p["id"] != args.id]
        if len(prompts) < before:
            save_library(prompts)
            print(f"{GREEN}✓ Removed '{args.id}'{RESET}")
        else:
            print(f"Prompt '{args.id}' not found.")
    
    elif args.command == "tags":
        all_tags = {}
        for p in prompts:
            for t in p.get("tags", []):
                all_tags[t] = all_tags.get(t, 0) + 1
        for tag, count in sorted(all_tags.items(), key=lambda x: -x[1]):
            print(f"  {CYAN}{tag:<20}{RESET} ({count})")
    
    elif args.command == "export":
        output = json.dumps(prompts, indent=2)
        if args.file:
            Path(args.file).write_text(output)
            print(f"Exported {len(prompts)} prompts to {args.file}")
        else:
            print(output)
    
    elif args.command == "import":
        new_prompts = json.loads(Path(args.file).read_text())
        existing_ids = {p["id"] for p in prompts}
        added = 0
        for np in new_prompts:
            if np.get("id") and np["id"] not in existing_ids:
                prompts.append(np)
                added += 1
        save_library(prompts)
        print(f"{GREEN}✓ Imported {added} new prompts ({len(new_prompts) - added} duplicates skipped){RESET}")
    
    elif args.command == "reset":
        save_library(list(BUILTIN_PROMPTS))
        print(f"{GREEN}✓ Library reset to {len(BUILTIN_PROMPTS)} built-in prompts{RESET}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
