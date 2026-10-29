# Development plan

1. Requirements gate: read both PDFs, map all features and deliverables, record ambiguity. Complete.
2. Build a Python package separating immutable measurement models, Windows ICMP transport, authorized discovery, statistics, rules and report output. Use real interface masks, IPv4 scope bounds, bounded probes and cancellation.
3. Build six Tkinter views. Capture inputs on the UI thread, run workers with a queue, poll results with after, and prevent overlapping jobs. Never update widgets in workers.
4. Execute pytest with deterministic injected transports. Record full logs and JUnit XML. Test failures are retained with fixes and rerun results. Perform offline GUI smoke verification separately.
5. Only after explicit scope authorization, collect local interface details and bounded real measurements. Preserve original evidence privately, avoid including private network records in submission by default. If unavailable, document exact manual steps.
6. Generate proposal, progress report, 8-12 page technical report, diagrams, 10-15 slide presentation, and 5-10 minute script using actual verified results. Render and visually inspect artifacts. Use PDF skill and presentation skill where supported.
7. Build and inspect the archive with exact required root folders, no technical documentation or private live evidence. Check imports, tests, artifact page/slide counts and ZIP integrity. Label pending video/name/template/live results honestly.

Architecture: GUI -> service functions -> Windows ICMP API and interface provider; services -> dataclasses -> statistics/rules -> text/JSON/PDF writers. Tests replace OS/network boundaries. Dependencies: psutil for interface metadata; optional reportlab for PDF export; pytest for development.

Release gates: no fabricated measurements, no unauthenticated scope expansion, no tests reported passed before execution, no Teams submission, no claim of fully submission-ready status while mandatory evidence/video/template requirements remain.
