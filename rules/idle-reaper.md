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
