#!/usr/bin/env bash
# Claude Code Rules installer: puts the rules in rules/ into a managed block in your CLAUDE.md.
#   ./install.sh                              the default rules, into ~/.claude/CLAUDE.md
#   ./install.sh --rules git,em-dashes        exactly these rules ("all" for every one)
#   ./install.sh --file ./CLAUDE.md           another CLAUDE.md, for example a project's
#   ./install.sh --simulator "iPhone 17"      the simulator model the simulator rules name
#   ./install.sh --companions all|none        companion paragraphs regardless of what is installed
#   ./install.sh --list                       the rules, and which companion tools are installed
#   ./install.sh --print                      print the block instead of writing it
#   ./install.sh --uninstall                  remove the managed block, keep everything else
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-}" in
  -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
esac

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required (macOS: xcode-select --install)" >&2; exit 1; }

exec python3 "$HERE/rules.py" "$@"
