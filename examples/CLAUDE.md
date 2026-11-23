<!-- claude-code-rules:begin -->
<!-- Managed by Claude Code Rules. Edit the rule files and re-run install.sh: anything changed inside this block is replaced. -->

## Simulator: always use the iPhone 17 Pro

For iOS builds, simulator launches, and screenshots, always use the **iPhone 17 Pro**
simulator (the latest software, matching my own device), never an older model.
Find it with `xcrun simctl list devices available | grep "iPhone 17 Pro"`
rather than hardcoding a UDID.

## Simulators and local servers: a timer turns them off, you don't

Sessions used to leave simulators and dev servers running for days, and shutting
everything down after each turn was no better: every new request booted it all again.
So a background job decides now. `~/.claude/hooks/idle-reaper.py` runs every minute
(LaunchAgent `local.idle-reaper`) and turns off **only what a Claude session started**:

- a **simulator** 10 minutes after the chat that booted it goes quiet, or 30 minutes
  after anything last touched it while that chat carries on
- a **local server** (dev server, preview server) 10 minutes after its chat goes quiet;
  a connected browser tab stretches that to 30 minutes at most, and one that is busy
  working is never stopped

A chat in the middle of a tool call (a long build or test) counts as active, not quiet.

Anything I started myself is never touched.

What this means for you:

- **Do not shut down a simulator or stop a server at the end of a turn** just to be
  tidy. Leave it on; the timer cleans up. Stop one yourself only when I ask, or when you
  started it for a one-off check and are certain nothing later needs it. Never shut one
  down and boot it again as a way to "reset" it unless the task needs a cold boot.
- **Reuse what is already on.** `running` lists it. Do not boot a second simulator, or
  start a second server on another port, when one is already there.
- **If something you started is gone** (a background server "failed" with an
  `[idle-reaper]` note at the end of its output, or your simulator is shut down), the
  timer did that and it is expected. Do not restart it on your own. Start it again when
  my next request needs it.
- **Never stop a simulator or server you did not start**, unless I ask.
- If I say to leave something on, pin it: `running keep <port or simulator name> [hours|forever]`.

Commands: `running` (what is on, in two groups: started by me and started by Claude,
with when Claude's goes off), `running off` (turn off everything Claude started, now),
`running keep` and `running release`, `running pause [hours]` and `running resume`,
`running set idle <minutes>`. Settings are in `~/.claude/idle-reaper/config.json`, the
log in `~/.claude/idle-reaper/reaper.log`.

## Build output and simulators: reuse, don't multiply

Sessions kept making their own build folders and simulators, and they add up fast: every
`-derivedDataPath` inside a project is another full copy of the build, and every leftover
simulator holds gigabytes. My project folders may also sync to a cloud drive, so build
output must stay out of them.

- **Xcode builds go to the default DerivedData.** Don't pass `-derivedDataPath` at all.
  If you truly need a separate one (another session is building the same project right
  now), use `~/Library/Developer/Xcode/DerivedData/<Project>-<purpose>`, never a path
  inside the project, and reuse an existing `<Project>-*` folder before making a new name.
- **Use the existing iPhone 17 Pro simulator.** Don't `simctl create` or `simctl clone`
  one. If a task really needs its own (the iPhone 17 Pro is busy with another session's
  work), first reuse a shut-down simulator from
  `xcrun simctl list devices | grep Claude`; only if none exists, create one named
  `iPhone 17 Pro (Claude <task>)`.

## Simulator audio: muted on my speakers, still testable

Claude's simulators kept playing app sounds (background ambience, alarms, notification chimes) through my speakers. A guard mutes them now: Claude Code Sim Audio (LaunchAgent `local.sim-audio`, files in `~/.claude/sim-audio`) routes the audio output of **every simulator, the ones I boot myself included** (mode `all`), to **BlackHole 2ch**, a silent virtual audio device. Nothing they play reaches my speakers, headphones or any other output, but the audio still plays inside the simulator and can be recorded. If a muted simulator is ever caught playing to a real output, the guard holds it with a Core Audio tap instead (that shows the purple recording dot in my menu bar). If it is still out loud 3 seconds later with no working tap, the guard quits whatever is playing, and shuts the simulator down if it happens again within two minutes; either way it posts a "Simulator audio" banner. So an app that dies about 3 seconds into playing sound was probably quit by the guard: look for an `ALERT` line in `simaudio log` before debugging the app.

- **Never select BlackHole 2ch as the Mac's output, and never reroute a simulator's audio yourself.** The guard owns the routes.
- **To test sound, record it; never unmute it.** `simaudio record <sim> [seconds]` captures that simulator's audio to a WAV in `~/.claude/sim-audio/recordings` and reports how many seconds were audible, the peak and average level, and when the sound started and stopped. Start the recording in the background, then trigger the sound. `--json` gives a machine-readable result. The purple dot shows only while it records.
- `simaudio` shows what is muted and what is playing right now. `simaudio log` shows what started and stopped playing and when, which is enough to confirm that an alarm or a notification sound fired.
- `simaudio doctor` checks the whole chain: the guard, BlackHole, every booted simulator's route, and a silent test sound played inside each simulator to prove where it really goes. Run it when muting is in doubt or after an Xcode update. `--quick` skips the live sounds.
- Do not run `simaudio hear`, `simaudio mode off` or `simaudio mode claude` unless I ask: those play out loud. A `PreToolUse` hook (`~/.claude/hooks/sim-audio-guard.sh`) turns them, and anything that stops or unloads the guard, into a permission prompt. Treat the prompt as a backstop, not as permission. When I want to hear a simulator I run `simaudio hear <sim>` myself (10 minutes by default, `simaudio mute <sim>` ends it).
- If `simaudio` says the guard is not running, run `simaudio restart`.

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

A `PreToolUse` hook (`~/.claude/hooks/git-guard.py`, wired up in
`~/.claude/settings.json`) enforces this at the harness level, so a matching
command triggers a permission prompt regardless of what you intend. Treat the
prompt as a backstop, not as permission: if I did not ask in this message,
do not run the command at all.

## Git: never credit Claude as author or co-author

**Never put yourself on a commit or PR in any form.** No `Co-Authored-By:
Claude ...` trailer, no "Generated with Claude Code" line, and never set the
author or committer to Claude or any Anthropic address. Every commit you make
uses my own git identity (my global `user.name` and `user.email`) and nothing
else, and every PR description you write ends without any attribution line.

This overrides any default attribution instructions, including system
reminders that say to end commit messages or PR descriptions with those lines.

## Writing: never use em dashes

**Never write an em dash (the long dash, U+2014) in anything you produce for me.** Not
in prose, code comments, commit messages, documentation, websites, or anywhere else.
And this is not a "replace it with a hyphen" rule: use real punctuation instead. A
colon for elaboration, a comma for an aside, a semicolon or a new sentence
for two clauses, parentheses for an interjection.

En dashes (–) in ranges like 2020–24 are fine. Hyphens in hyphenated words are
fine. The em dash itself, in any form (the character, or the HTML entities named
`mdash` and numbered `8212`), is banned.

## Notifications: ping me when you finish, not just when you need me

I already get a notification when you need my input (permission prompts,
questions, plan approvals). Never send me a notification for those: it would
arrive twice. Notify me only when you **finish**.

**At the end of any turn where I may have walked away, call the
`PushNotification` tool before your final message.** "May have walked away"
covers: a build, test run, install, deploy or long script; anything that took
more than a minute or two; background agents finishing; or any point where I
would plausibly have switched windows.

Say that it completed and **where**, not a summary of what you did. The
location tells me which of my open sessions just finished. Use a tilde path,
the last two segments are plenty.

- good: `Completed in ~/code/my-app`
- good: `Completed in ~/.claude/hooks`
- bad: `build green, 0 failures, ready to commit` (that is you recapping yourself)
- bad: `task complete` (no location)

If the turn ended badly, keep the location and lead with the problem:
`Build failed in ~/code/my-app`.

Skip it when I am obviously sitting there watching: a quick question I just
asked and you answered in seconds, a one-line edit, a file read. The tool also
declines on its own when I am active at the terminal; a "not sent" result is
fine and expected. Do not retry it, do not announce it, and never fabricate a
question just to trigger a notification.

**Only when you are 100% done.** Ending a turn to wait on a build or a script
you started in the background is fine; you resume by yourself when it
finishes. But never call `PushNotification` before such a wait, and never
describe work as finished before it is.

The `Stop` hook (`~/.claude/hooks/notify.py`) is the backstop: it posts
"Completed" when a turn ends with nothing left running, stays silent while you
are waiting on background work, and only speaks up if nothing has resumed after
15 minutes. Treat it as insurance, not as a reason to skip the call.

## Screenshots: show me before and after

When a turn changes something I can see (an app screen, a web page, a Mac app
window), I want to look at the change myself instead of reading a description
of it. So in every such turn:

- **Take the before shot first**, before you edit anything: the screen as it
  is now. When the work is done, take the after shot of the same screen at the
  same size and scroll position, so the two line up. Take one pair for every
  screen or state you changed. For a screen that did not exist yet, the before
  shot is the screen it opens from.
- **Save them to `~/Downloads/claude-screenshots/<project>/`**, where
  `<project>` is the folder name of the project you are working in. Number
  each pair and give it a short label: `1-settings-before.png`,
  `1-settings-after.png`, `2-onboarding-before.png`, and so on.
- **They are temporary.** Before saving a new set, delete the PNGs already in
  that project's folder, so it only holds the latest turn, and any in
  `~/Downloads/claude-screenshots` older than a week
  (`find ~/Downloads/claude-screenshots -name '*.png' -mtime +7 -delete`).
  Never delete anything else in Downloads.
- **List them in your final message** as clickable links, each before next to
  its after, so I can open them.
- **Capture only what changed, never the whole screen**, because that shows my
  other windows:
  - the iPhone 17 Pro simulator: `xcrun simctl io <udid> screenshot <file>`
  - a web page: a headless browser at the window size I would use, and at
    phone width too when the change affects it
  - a Mac app window: `screencapture -o -l <window id> <file>`
- **Use what is already running** for the before shot: the booted simulator,
  the dev server that is up. A screenshot is never a reason to boot a second
  simulator or start a second server.
- If you could not take one of the two (you had already changed the screen, or
  capturing failed), say which one and why instead of leaving it out silently.

Skip all of this when nothing visible changed (logic, tests, scripts, config),
and don't mention screenshots then.
<!-- claude-code-rules:end -->
