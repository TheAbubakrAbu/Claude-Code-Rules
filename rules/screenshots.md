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
  - the {{SIMULATOR}} simulator: `xcrun simctl io <udid> screenshot <file>`
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
