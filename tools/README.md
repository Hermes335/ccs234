# Project maintenance tools

These scripts preserve the authoring and verification work independently of the ignored .build folder. Run them from the project root. They are not needed to run the desktop application.

- package_project.py: rebuilds the submission ZIP and validates its structure. The separate technical documentation is excluded from the course ZIP, while it remains versioned in Git.
- build_documents.py: regenerates academic PDFs from the original local evidence. Requires ReportLab and Windows Times New Roman fonts.
- build_presentation.mjs and render_final_deck.mjs: reproduce the deck using the bundled Codex artifact runtime. Their runtime paths describe the original authoring environment and may need adjustment on another machine.
- gui_smoke.py: exercises Tkinter offline with mocked data.
- capture_gui.py: captures the actual application while displaying saved live data. Does not send probes.
- validate_live.py: historical capture helper tied to the originally authorized subnet. Do not run it on another network or assume it grants new authorization.
- sync-repository.ps1: safe, pull-only updater, described in GITHUB_SYNC.md.
- test_sync_repository.py: offline integration tests using temporary local Git repositories; no GitHub or network requests.

Run updater tests with:

```powershell
.\SourceCode\.venv\Scripts\python.exe -m pytest -q tools/test_sync_repository.py
```

Temporary dependencies, rendered previews and local sync state stay outside Git. Do not commit credentials or new private evidence without reviewing the repository's public visibility.
