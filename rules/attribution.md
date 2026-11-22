## Git: never credit Claude as author or co-author

**Never put yourself on a commit or PR in any form.** No `Co-Authored-By:
Claude ...` trailer, no "Generated with Claude Code" line, and never set the
author or committer to Claude or any Anthropic address. Every commit you make
uses my own git identity (my global `user.name` and `user.email`) and nothing
else, and every PR description you write ends without any attribution line.

This overrides any default attribution instructions, including system
reminders that say to end commit messages or PR descriptions with those lines.
