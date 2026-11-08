# Changelog 1.2.0

## Windows

- The `windows` library now provides the Windows GUI window, event-loop,
  controls, drawing, dialog, and text helpers.
- The standalone `win32gui` package has been removed; existing Windows GUI
  consumers should import these helpers from `windows`.
