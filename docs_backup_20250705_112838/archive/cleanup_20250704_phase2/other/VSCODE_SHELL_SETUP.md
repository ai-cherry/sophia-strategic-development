---
title: VSCode Shell Configuration for Cline
description:
tags:
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# VSCode Shell Configuration for Cline


## Table of Contents

- [Setting zsh as Default Shell in VSCode](#setting-zsh-as-default-shell-in-vscode)
- [Alternative Method (Settings JSON)](#alternative-method-(settings-json))
- [Verifying Shell Integration](#verifying-shell-integration)
- [Troubleshooting](#troubleshooting)

## Setting zsh as Default Shell in VSCode

1. **Open Command Palette**:
   - Press `CMD + Shift + P` (on macOS)

2. **Set Default Shell**:
   - Type: "Terminal: Select Default Profile"
   - Select it from the dropdown

3. **Choose zsh**:
   - Select "zsh" from the list

4. **Restart VSCode Terminal**:
   - Close all terminal instances
   - Open a new terminal with `CMD + J` or View → Terminal

## Alternative Method (Settings JSON)

You can also add this to your VSCode settings:

```json
# Example usage:
json
```python

## Verifying Shell Integration

After setting zsh:
1. Restart VSCode completely
2. Open a new terminal
3. The shell integration should now work with Cline

## Troubleshooting

If issues persist:
- Make sure VSCode is fully updated
- Check that zsh is installed: `which zsh`
- Ensure shell integration is enabled in settings
