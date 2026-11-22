## Simulator: always use the {{SIMULATOR}}

For iOS builds, simulator launches, and screenshots, always use the **{{SIMULATOR}}**
simulator (the latest software, matching my own device), never an older model.
Find it with `xcrun simctl list devices available | grep "{{SIMULATOR}}"`
rather than hardcoding a UDID.
