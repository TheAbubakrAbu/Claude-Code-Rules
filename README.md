# Claude Code Rules

**A starter `CLAUDE.md` for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), where every rule exists because something went wrong without it, plus an installer that adds the rules without touching what you already wrote.** Nine rules on simulators, build output, git, attribution, writing, notifications, and screenshots, four of them paired with a tool that enforces or supports them.

[![tests](https://github.com/TheAbubakrAbu/Claude-Code-Rules/actions/workflows/tests.yml/badge.svg)](https://github.com/TheAbubakrAbu/Claude-Code-Rules/actions/workflows/tests.yml)

Created by **Abubakr Elmallah** on **November 22, 2026**.

## At a glance

| | |
|---|---|
| **9** rules | one Markdown file each, in [rules/](rules) |
| **4** companion tools | Notify, Git Guard, Idle Reaper, Sim Audio |
| **1** managed block | everything outside it in your `CLAUDE.md` is never changed |
| **0** dependencies | Python 3.8+, standard library only |
| **34** tests | run on macOS and Ubuntu on every push |

---

## Table of Contents

- [Why this exists](#why-this-exists)
- [The rules](#the-rules)
- [Getting Started](#getting-started)
- [Commands](#commands)
- [How it works](#how-it-works)
- [Companion tools](#companion-tools)
- [Writing your own rule](#writing-your-own-rule)
- [Known Limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Privacy & Data](#privacy--data)
- [Testing](#testing)
- [Uninstall](#uninstall)
- [License](#license)
- [Feedback & Contact](#feedback--contact)

---

## Why this exists

**Every rule here was written the day after the thing it prevents.**

Left to their defaults, Claude Code sessions on one Mac produced:

- a **29 GB `build/` folder** inside one iOS project, about 15 full copies of the same build, each session having made its own `-derivedDataPath`;
- **19 leftover simulators holding 93 GB**, because each session created a fresh one instead of reusing the one that was there;
- **eight headless simulators running for days**, until the Mac overheated; and when sessions were told to shut everything down at the end of each turn instead, the next request booted it all again;
- **app sounds playing through the speakers** from simulators nobody was looking at;
- **commits and pushes nobody asked for**, because a task "seemed to require it" or a commit was approved three messages earlier;
- **"Co-Authored-By" trailers** on commits that were supposed to carry one person's name;
- **em dashes in everything**, from commit messages to websites;
- **screen changes described only in words**, so seeing one meant building and opening the app by hand;
- **notifications that arrived twice** for every question, once from a hook and once from Claude Code itself.

A rule in `CLAUDE.md` is how you tell Claude about each of these once instead of every session. This repository is those rules, written so they work on anyone's machine, with an installer that keeps them in one managed block you can update or remove without touching anything you wrote yourself.

## The rules

| Id | Rule | Companion tool |
| --- | --- | --- |
| `simulator` | Use one simulator model (the iPhone 17 Pro by default) for every iOS build, launch, and screenshot | |
| `idle-reaper` | Leave simulators and dev servers on at the end of a turn; a timer turns off what Claude started once it goes idle | [Idle Reaper](https://github.com/TheAbubakrAbu/Claude-Code-Idle-Reaper) (required) |
| `build-output` | Build into the default DerivedData, never into the project; reuse the existing simulator instead of creating one | |
| `sim-audio` | Simulator audio is muted; record it to test sound, never unmute or reroute it | [Sim Audio](https://github.com/TheAbubakrAbu/Claude-Code-Sim-Audio) (required) |
| `git` | Never commit, push, or rewrite history unless asked in that very message; show the exact commit first | [Git Guard](https://github.com/TheAbubakrAbu/Claude-Code-Git-Guard) (optional) |
| `attribution` | Never credit Claude as author or co-author of a commit or PR | |
| `em-dashes` | Never write an em dash; use a colon, comma, semicolon, or parentheses | |
| `notifications` | Push a notification when the work is finished, with where it finished; never for a question | [Notify](https://github.com/TheAbubakrAbu/Claude-Code-Notify) (optional) |
| `screenshots` | For every visible change, save a before and an after screenshot to `~/Downloads/claude-screenshots` and link them | |

Read them all assembled in [examples/CLAUDE.md](examples/CLAUDE.md).

## Getting Started

1. **Clone the project:**

   ```bash
   git clone https://github.com/TheAbubakrAbu/Claude-Code-Rules.git
   cd Claude-Code-Rules
   ```

2. **See what would be installed:**

   ```bash
   ./install.sh --list
   ```

   It lists every rule and whether its companion tool is installed on this machine.

3. **Install:**

   ```bash
   ./install.sh                                # or: ./install.sh --simulator "iPhone Air"
   ```

   It adds the default rules to `~/.claude/CLAUDE.md` in a managed block: every rule that needs no tool, plus `idle-reaper` and `sim-audio` once their tools are installed. A backup of `CLAUDE.md` is written first, and running it again changes nothing.

4. **Restart your Claude Code sessions.** `CLAUDE.md` is read when a session starts.

## Commands

| Command | Description |
| --- | --- |
| `./install.sh` | Install the default rules into `~/.claude/CLAUDE.md` |
| `./install.sh --rules git,em-dashes` | Install exactly these rules; `--rules all` for every one |
| `./install.sh --simulator "NAME"` | The simulator model the `simulator` and `build-output` rules name (default `iPhone 17 Pro`) |
| `./install.sh --file PATH` | Manage another `CLAUDE.md`, for example a project's |
| `./install.sh --companions all` | Include the paragraphs about companion tools even when the tool is not installed (`none` leaves them out, `detect` is the default) |
| `./install.sh --print` | Print the block to the terminal instead of writing it |
| `./install.sh --list` | List the rules and which companion tools are installed |
| `./install.sh --uninstall` | Remove the managed block, keep everything else |

## How it works

The installer writes the rules between two markers:

```markdown
<!-- claude-code-rules:begin -->
<!-- Managed by Claude Code Rules. Edit the rule files and re-run install.sh: anything changed inside this block is replaced. -->

## Simulator: always use the iPhone 17 Pro
...
<!-- claude-code-rules:end -->
```

- **Your text is never touched.** Everything before and after the block stays exactly as it was. In a new file, the block is all there is; in an existing one, it goes at the end, one blank line after your text.
- **Nothing is added twice.** If a rule's heading already appears outside the block (you wrote that rule by hand, under the same heading, in any letter case), the rule is skipped and the installer says so. A `CLAUDE.md` that already holds every rule gets nothing added.
- **Re-running replaces the block.** Changing `--rules` or `--simulator`, or pulling a newer version of the rules, rewrites the block in place. Edits you make inside the block are replaced; put your own rules outside it.
- **Companion paragraphs follow the tool.** The `git` and `notifications` rules work on their own, and each ends with a paragraph about its hook. That paragraph is included only when the hook is installed, so Claude is never told about a hook that is not there.
- **Backups first.** Every change writes `CLAUDE.md.bak-<time>` first.
- **Uninstalling restores your file.** `--uninstall` removes the block and the blank line before it. If the file held nothing else, it is deleted.

## Companion tools

| Tool | What it does | Rules |
| --- | --- | --- |
| [Claude Code Notify](https://github.com/TheAbubakrAbu/Claude-Code-Notify) | A `Stop` hook that tells you when Claude is actually done, not every time it waits on a build | `notifications` |
| [Claude Code Git Guard](https://github.com/TheAbubakrAbu/Claude-Code-Git-Guard) | A `PreToolUse` hook that makes every commit, push, and history rewrite a permission prompt | `git` |
| [Claude Code Idle Reaper](https://github.com/TheAbubakrAbu/Claude-Code-Idle-Reaper) | A timer that turns off the simulators and dev servers Claude started once they go idle, and the `running` command | `idle-reaper` |
| [Claude Code Sim Audio](https://github.com/TheAbubakrAbu/Claude-Code-Sim-Audio) | A guard that routes simulator audio to a silent device, and the `simaudio` command to record and check it | `sim-audio` |

A rule tells Claude what to do; the companion makes sure of it, or does the work itself. The installer finds a companion by its default install path, such as `~/.claude/hooks/git-guard.py`.

## Writing your own rule

1. Add `rules/<id>.md`, starting with a `## ` heading. Write it to Claude, in the first person ("my speakers", "unless I ask"), and give the reason before the instruction: Claude follows a rule better when it knows what went wrong without it.
2. Add an entry to [rules/index.json](rules/index.json) with its `id`, `file`, and a one-line `summary`. If a tool goes with it, add a `companion` with `name`, `url`, `required`, and the `detect` paths that show it is installed.
3. For an optional companion, put the paragraphs about the tool after a `<!-- companion: Name -->` line.
4. Use `{{SIMULATOR}}` wherever the simulator model belongs.
5. Regenerate the example and run the tests:

   ```bash
   python3 rules.py --print --rules all --companions all > examples/CLAUDE.md
   python3 -m unittest discover -s tests -v
   ```

## Known Limitations

- **A rule is guidance, not enforcement.** Claude reads `CLAUDE.md` and usually follows it; a hook is what makes sure. That is what the companion tools are for.
- **Duplicates are found by heading only.** A rule you wrote under a different heading is not recognized, and you get both. Read `--print` first, or skip a rule with `--rules`.
- **Edits inside the block do not survive a re-run.** Change the rule file, or write your version outside the block.
- **Four of the rules are about iOS simulators and Xcode.** They are harmless elsewhere but only useful on a Mac that builds for iOS; leave them out with `--rules`.
- **Companions are found at their default paths.** A tool installed somewhere else reads as not installed; use `--rules` and `--companions all`.
- **Sessions read `CLAUDE.md` when they start.** Restart open sessions after a change.

## Troubleshooting

- **A rule did not appear.** Run `./install.sh --list`: `idle-reaper` and `sim-audio` are installed by default only once their tool is. The installer also prints `skipped <id>` for every rule it found already written outside the block.
- **"the managed block markers are broken".** One of the two marker lines was deleted or duplicated. Fix them by hand (or delete the block's remains), then run the installer again; it refuses to guess.
- **I want my own wording.** Write the rule outside the block under the same heading; the installer will skip its own copy.

## Privacy & Data

**Claude Code Rules** stays on your machine:
- **What it reads:** the rule files in this repository, your `CLAUDE.md`, and whether the companion tools' files exist.
- **What it writes:** your `CLAUDE.md` and its `CLAUDE.md.bak-<time>` backups. Nothing else, and no network access.

## Testing

```bash
python3 -m unittest discover -s tests -v       # 34 tests, HOME is a temp folder
./install.sh --print --rules all               # read exactly what would be installed
```

The tests check that every rule file is listed once with a unique heading, that companion paragraphs appear only where a tool is optional and only when it is installed, that [examples/CLAUDE.md](examples/CLAUDE.md) matches the rules, and that the installer keeps your text, skips rules you already wrote, backs up before every change, refuses broken markers, and restores the file exactly on uninstall. A hygiene test keeps em dashes, home-folder paths, and signing identities out of the repository. The [GitHub Actions workflow](.github/workflows/tests.yml) runs the suite on macOS and Ubuntu and exercises the installer end to end.

## Uninstall

```bash
./install.sh --uninstall                      # removes the managed block, keeps your text
./install.sh --uninstall --file PATH          # the same for another CLAUDE.md
```

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code, but please provide attribution.

## Feedback & Contact

I'd love to hear your thoughts! Open an issue, or reach out with feedback, feature requests, or questions:
- **Email:** contact@abubakrelmallah.com
- **Website:** [abubakrelmallah.com](https://abubakrelmallah.com/)
- **LinkedIn:** [Abubakr Elmallah](https://www.linkedin.com/in/abubakr-elmallah-416a0b273/)
