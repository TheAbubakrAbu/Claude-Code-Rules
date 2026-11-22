## Build output and simulators: reuse, don't multiply

Sessions kept making their own build folders and simulators, and they add up fast: every
`-derivedDataPath` inside a project is another full copy of the build, and every leftover
simulator holds gigabytes. My project folders may also sync to a cloud drive, so build
output must stay out of them.

- **Xcode builds go to the default DerivedData.** Don't pass `-derivedDataPath` at all.
  If you truly need a separate one (another session is building the same project right
  now), use `~/Library/Developer/Xcode/DerivedData/<Project>-<purpose>`, never a path
  inside the project, and reuse an existing `<Project>-*` folder before making a new name.
- **Use the existing {{SIMULATOR}} simulator.** Don't `simctl create` or `simctl clone`
  one. If a task really needs its own (the {{SIMULATOR}} is busy with another session's
  work), first reuse a shut-down simulator from
  `xcrun simctl list devices | grep Claude`; only if none exists, create one named
  `{{SIMULATOR}} (Claude <task>)`.
