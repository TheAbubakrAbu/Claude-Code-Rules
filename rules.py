#!/usr/bin/env python3
"""
Claude Code Rules: puts the rules in rules/ into a managed block in your CLAUDE.md.

  rules.py                            install the default rules into ~/.claude/CLAUDE.md
  rules.py --rules git,em-dashes      install exactly these rules ("all" for every one)
  rules.py --file PATH                use another CLAUDE.md, for example a project's
  rules.py --simulator "iPhone 17"    the simulator model the simulator rules name
  rules.py --companions all|none      companion paragraphs regardless of what is installed
  rules.py --print                    print the block instead of writing it
  rules.py --list                     list the rules and which companion tools are installed
  rules.py --uninstall                remove the managed block

Everything outside the block is yours and is never changed. A rule whose heading already
appears outside the block (you wrote it by hand) is skipped, so nothing is added twice.
"""
import argparse
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(ROOT, "rules")
BEGIN = "<!-- claude-code-rules:begin -->"
END = "<!-- claude-code-rules:end -->"
NOTE = ("<!-- Managed by Claude Code Rules. Edit the rule files and re-run install.sh: "
        "anything changed inside this block is replaced. -->")
COMPANION_MARK = "<!-- companion"
DEFAULT_SIMULATOR = "iPhone 17 Pro"


class RulesError(Exception):
    pass


def home():
    return os.environ.get("HOME") or os.path.expanduser("~")


def expand(path):
    return home() + path[1:] if path.startswith("~") else path


def load_rules():
    with open(os.path.join(RULES_DIR, "index.json"), encoding="utf-8") as fh:
        return json.load(fh)["rules"]


def read_rule(rule):
    """The rule's text and its companion part (the paragraphs after the companion marker)."""
    with open(os.path.join(RULES_DIR, rule["file"]), encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(COMPANION_MARK):
            return "\n".join(lines[:i]).strip(), "\n".join(lines[i + 1:]).strip()
    return text.strip(), ""


def heading(text):
    for line in text.splitlines():
        if line.startswith("## "):
            return line.strip()
    return ""


def companion_installed(rule):
    companion = rule.get("companion")
    return bool(companion) and any(os.path.exists(expand(p)) for p in companion.get("detect", []))


def select(rules, spec):
    """The rules to install: by default every rule that needs no tool, plus the ones whose
    tool is installed; "all"; or a comma-separated list of ids."""
    if spec is None:
        return [r for r in rules
                if not (r.get("companion") or {}).get("required") or companion_installed(r)]
    if spec.strip() == "all":
        return list(rules)
    wanted = [s.strip() for s in spec.split(",") if s.strip()]
    ids = [r["id"] for r in rules]
    unknown = [w for w in wanted if w not in ids]
    if unknown:
        raise RulesError("unknown rule: %s (known: %s)" % (", ".join(unknown), ", ".join(ids)))
    return [r for r in rules if r["id"] in wanted]


def render_rule(rule, simulator, companions):
    body, extra = read_rule(rule)
    include = companions == "all" or (companions == "detect" and companion_installed(rule))
    if extra and include:
        body = body + "\n\n" + extra
    return body.replace("{{SIMULATOR}}", simulator)


def render_block(texts):
    return "\n".join([BEGIN, NOTE, "", "\n\n".join(texts), END])


def split_managed(text):
    """(before, block, after) when the file holds a managed block, else (text, None, "")."""
    begins, ends = text.count(BEGIN), text.count(END)
    if begins == 0 and ends == 0:
        return text, None, ""
    if begins != 1 or ends != 1 or text.index(BEGIN) > text.index(END):
        raise RulesError("the managed block markers are broken (%d begin, %d end); "
                         "fix them by hand first" % (begins, ends))
    start = text.index(BEGIN)
    stop = text.index(END) + len(END)
    return text[:start], text[start:stop], text[stop:]


def join(before, block, after):
    """Put the block back between `before` and `after`, one blank line from each."""
    before = before.rstrip("\n")
    after = after.lstrip("\n")
    parts = [p for p in (before, block, after.rstrip("\n")) if p]
    return "\n\n".join(parts) + "\n" if parts else ""


def read_file(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def write_file(path, text, original):
    if original is not None:
        backup = path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
        n = 1
        while os.path.exists(backup):  # two runs in one second must not share a backup
            backup = path + ".bak-" + time.strftime("%Y%m%d-%H%M%S") + "-%d" % n
            n += 1
        shutil.copy(path, backup)
        print("backed up " + backup)
    if text:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    elif original is not None:
        os.remove(path)
        print("removed " + path + " (nothing was left in it)")


def plan(path, spec, simulator, companions):
    """Work out the new file: returns (original, new_text, installed_ids, skipped)."""
    original = read_file(path)
    before, _block, after = split_managed(original or "")
    outside = (before + "\n" + after).lower().splitlines()
    outside = {line.strip() for line in outside}
    texts, installed, skipped = [], [], []
    for rule in select(load_rules(), spec):
        text = render_rule(rule, simulator, companions)
        if heading(text).lower() in outside:
            skipped.append((rule["id"], heading(text)))
            continue
        texts.append(text)
        installed.append(rule["id"])
    if not texts and _block is None:
        return original, original or "", installed, skipped  # nothing to add, nothing to remove
    block = render_block(texts) if texts else ""
    return original, join(before, block, after), installed, skipped


def install(path, spec, simulator, companions):
    original, text, installed, skipped = plan(path, spec, simulator, companions)
    for rule_id, head in skipped:
        print("skipped %s: %s already has %r outside the managed block" % (rule_id, path, head))
    if text == (original or ""):
        print(("already up to date: " if installed else "nothing to add to ") + path)
        return 0
    write_file(path, text, original)
    if installed:
        print("wrote %d rule%s into %s: %s" % (len(installed), "" if len(installed) == 1 else "s",
                                             path, ", ".join(installed)))
    else:
        print("nothing to add to " + path)
    return 0


def uninstall(path):
    original = read_file(path)
    if original is None:
        print("nothing to remove: %s does not exist" % path)
        return 0
    before, block, after = split_managed(original)
    if block is None:
        print("nothing to remove: %s has no managed block" % path)
        return 0
    write_file(path, join(before, "", after), original)
    print("removed the managed block from " + path)
    return 0


def list_rules():
    rows = []
    for rule in load_rules():
        companion = rule.get("companion") or {}
        if not companion:
            state = "-"
        else:
            state = "%s %s%s" % (companion["name"],
                                 "installed" if companion_installed(rule) else "not installed",
                                 ", required" if companion.get("required") else "")
        rows.append((rule["id"], rule["summary"], state))
    width = max(len(r[0]) for r in rows)
    for rule_id, summary, state in rows:
        print("%s  %s" % (rule_id.ljust(width), summary))
        print("%s  companion: %s" % (" " * width, state))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(prog="install.sh", description=__doc__.split("\n\n")[0].strip())
    parser.add_argument("--file", default="~/.claude/CLAUDE.md", help="the CLAUDE.md to manage")
    parser.add_argument("--rules", help='comma-separated rule ids, or "all"')
    parser.add_argument("--simulator", default=DEFAULT_SIMULATOR, help="simulator model to name")
    parser.add_argument("--companions", choices=["detect", "all", "none"], default="detect",
                        help="include companion paragraphs: when the tool is installed, always, never")
    parser.add_argument("--print", dest="print_only", action="store_true", help="print the block only")
    parser.add_argument("--list", action="store_true", help="list the rules")
    parser.add_argument("--uninstall", action="store_true", help="remove the managed block")
    args = parser.parse_args(argv)
    path = expand(args.file)
    try:
        if args.list:
            return list_rules()
        if args.uninstall:
            return uninstall(path)
        if args.print_only:
            texts = [render_rule(r, args.simulator, args.companions)
                     for r in select(load_rules(), args.rules)]
            sys.stdout.write(render_block(texts) + "\n")
            return 0
        return install(path, args.rules, args.simulator, args.companions)
    except RulesError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
