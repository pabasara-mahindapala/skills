---
name: set-display
description: >
  Set the resolution and refresh rate of an external display on macOS via CoreGraphics,
  including modes that System Settings refuses to list. Use when a monitor is stuck at the
  wrong resolution or aspect ratio, when an ultrawide shows only 16:9 options, when the
  desired refresh rate is missing, or when the user wants to enumerate every mode a display
  actually supports. Keywords: display resolution, refresh rate, ultrawide, 3440x1440, hz,
  monitor stuck, wrong resolution, show all resolutions, aspect ratio, external monitor, EDID.
---

# Set Display Mode

Set macOS display modes directly through CoreGraphics, bypassing the System Settings UI.

## Why this exists

The Displays pane filters its resolution list to the aspect ratio it derives from the
display's EDID *preferred* timing. When a hub or adapter advertises a preferred timing that
does not match the panel (e.g. 1920x1080 on a 3440x1440 ultrawide), macOS hides every mode
of the real aspect ratio. Toggling "Show all resolutions" does not help — that toggle adds
low-resolution variants, it does not lift the aspect-ratio filter.

The modes are still present and fully usable in CoreGraphics. These tools reach them.

## Tools

Both live in `tools/` beside this file. Use absolute paths when invoking them.

| tool | usage |
|---|---|
| `listmodes` | no arguments — prints every mode of the first external display, marks the current one |
| `setmode` | `setmode <width> <height> <refresh>` — applies that mode permanently |

If a binary is missing or fails to run, rebuild it in `tools/`:

```
swiftc -O setmode.swift -o setmode
swiftc -O modes.swift -o listmodes
```

## Procedure

1. **Enumerate first.** Run `listmodes` and read the actual list. Never guess a mode —
   `setmode` exits non-zero with `mode WxH@R not available` if it is not offered.

2. **Read the output correctly.** Each line shows point size, backing pixels, and refresh:

   ```
   3440x1440   backing  3440x1440    99.00Hz              <- native, use this
   1720x720    backing  3440x1440    99.00Hz HiDPI        <- UI renders huge, rarely wanted
   ```

   `setmode` only matches native modes where point size equals backing size, so the HiDPI
   variants are not reachable through it by design.

3. **Apply the lowest safe refresh first**, confirm the display survives, then step up.
   The mode list reflects what the EDID advertises, not a guarantee the cable or hub
   sustains the bandwidth. An unsustainable mode gives a black screen.

4. **Verify** with `listmodes` again, or independently:

   ```
   system_profiler SPDisplaysDataType | grep -A5 "<display name>"
   ```

   Immediately after a change, `setmode` may print a placeholder size such as `1x1` while
   the link renegotiates. That is not a failure — re-query to get the settled value.

## Recovery

A mode that the hardware cannot sustain blanks the screen. Unplug and replug the display
cable; macOS falls back to a safe mode. Warn the user before applying a refresh rate that
has not been confirmed working, so they can be at the machine to do this.

## Scope and limits

- Targets **the first non-builtin display only**. With two or more external monitors it will
  pick whichever CoreGraphics enumerates first, which may not be the intended one. Extend
  `setmode.swift` to select by display ID if that case comes up.
- Changes are applied with `.permanently`, so they persist across reboots and replugs.
- The mode stays absent from the System Settings list — this sets the mode, not the UI filter.
- Refresh rate ceilings are a link property. If the desired rate is not in `listmodes` at all,
  no software can add it; that needs a different cable, port, or a direct connection instead
  of a hub.
