## Git: never commit or push unless explicitly told to, in that message

**Do not run `git commit`, `git push`, or anything that rewrites history or
mutates a remote unless I explicitly ask for it in the message I just sent.**

This is absolute. It is not overridden by:

- a task that seems to require it ("set up GitHub Pages", "deploy this",
  "publish the site"): do the work, then **stop and tell me it's ready to commit**
- me having asked you to commit earlier in the conversation: permission is
  per-message, it does not carry forward
- the repo being mine, the branch being `main`, or the change being small
- you being confident it's what I want

Specifically covered: `commit`, `push`, `merge`, `rebase`, `cherry-pick`,
`revert`, `am`, `tag`, `reset`, `filter-branch`/`filter-repo`, `remote add|rm|set-url`,
`branch -d|-D|-m|-M`, `clean -f`, and `gh pr|release|repo create|merge|edit|delete|close`.

Reading git state is always fine: `status`, `log`, `diff`, `show`, `remote -v`,
`branch --show-current`, `ls-files`, etc.

**What to do instead:** make the file changes, leave them uncommitted, and say
plainly what is staged/modified and what the commit would be. I will tell you
when to commit.

**Double-check even when I do ask.** When I explicitly and clearly tell you
to commit or push, don't run anything yet. First reply with exactly what will
happen: the files being staged, the full commit message, and the branch and
remote for a push. Run it only after I answer that summary with a clear yes,
and do only what you listed. Vague wording ("looks good", "ship it", "wrap
this up") is never a request to commit or push.

<!-- companion: Claude Code Git Guard -->
A `PreToolUse` hook (`~/.claude/hooks/git-guard.py`, wired up in
`~/.claude/settings.json`) enforces this at the harness level, so a matching
command triggers a permission prompt regardless of what you intend. Treat the
prompt as a backstop, not as permission: if I did not ask in this message,
do not run the command at all.
