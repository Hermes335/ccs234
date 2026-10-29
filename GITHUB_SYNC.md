# GitHub and local folder updates

Repository: https://github.com/Ralph51207/ccs234

This folder is the Git working copy. The intended automatic update policy is:

- Check origin/main every five minutes while the Windows user is logged in and the laptop is awake.
- Apply fast-forward updates only when the working tree is clean.
- Pause for local edits, untracked files, another checked-out branch, divergent history, network failures or changed origin configuration.
- Never discard, stash, overwrite or upload local changes automatically.
- Never execute newly downloaded project code or install dependencies automatically.

The scheduled task runs a local copy of tools/sync-repository.ps1 from the ignored .sync folder. Repository updates therefore cannot silently change the installed updater. Logs are written to .sync/auto-update.log. Existing local environments, build caches and sync state are ignored by Git and remain local.

The task registration name and verified installation state will be recorded below after setup.

## Manual commands

Run these from the project root:

```powershell
git status
git pull --ff-only
```

To publish your own deliberate edits:

```powershell
git add <files-you-reviewed>
git commit -m "Describe your change"
git push
```

If the updater reports a dirty or divergent working tree, inspect git status and reconcile the edits manually. It will not discard your work. If the laptop is off, asleep, logged out or offline, updates wait until it can run again. Normal files require no installation to refresh; changed Python dependencies still require a deliberate pip install using the project's requirements files.
