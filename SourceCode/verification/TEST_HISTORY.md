# Automated test history

2026-10-27 first invocation from workspace root: pytest collection failed with three ModuleNotFoundError errors for netmonitor. No test bodies executed. Initial JUnit XML retained as pytest-initial-collection-error.xml. Cause: SourceCode was not on Python's import path when invoked from its parent directory. Fix: add `pythonpath = .` to SourceCode/pytest.ini, resolved relative to the pytest root directory. Rerun results are recorded separately in pytest-output.txt and pytest-results.xml.

All fixtures in this folder are mocked; none are live measurements.

Clean installation verification: installed requirements-dev.txt into a newly created SourceCode/.venv, including ReportLab 4.5.1. The installed-environment run executed 64 tests successfully in 0.57 s. Its separate stdout and JUnit files are retained. `pip check` reported no broken requirements. The GUI integration checks were repeated after correcting the footer placement and adding the discovery scrollbar; seven checks passed without network access. These later checks verify the final GUI edits and actual installation instructions, not additional live measurements.
