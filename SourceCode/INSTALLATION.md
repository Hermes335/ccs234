# Installation and validation

See README.md for the exact PowerShell commands. Use a fresh virtual environment inside SourceCode, install requirements.txt and launch main.py. Runtime dependencies are psutil and reportlab; Tkinter is bundled with standard Windows Python. pytest is a development dependency only.

Validated platform: Windows, Python 3.10. Minimum supported Python: 3.10 (union type annotations). Live probes require Windows iphlpapi.dll. Test logic can run elsewhere, but desktop live transport is Windows-specific.

After launching, confirm all six tabs are present and that the startup state contains no measurements. Refresh adapters. Obtain permission before checking the authorization box. For a safe rehearsal, inspect the startup UI and export an empty report without checking authorization; missing measurements must remain N/A.

Acceptance checks: run pytest; perform four probes against an authorized local target; independently calculate mean, maximum and loss; save a report; open it and compare with the screen. Keep raw measurements private and record genuine timestamps.
