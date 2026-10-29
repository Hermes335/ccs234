# Test plan

## Automated mocked tests

All unit tests use synthetic fixtures/injected providers and make no network requests. Cover IPv4 and hostname validation; invalid numeric IPs, shell-like strings, IPv6 unsupported errors; valid/invalid scopes; no authorization; subnet limits; bounded counts/timeouts; ICMP success, timeout, unreachable and local transport errors; missing/zero latency; discovery results and cancellation; mean, maximum and loss; empty/no-response statistics; report timestamps and provenance; JSON/text/PDF saves; rule thresholds and non-diagnostic advice.

Separate sent-but-unanswered probes from local errors that may not have sent a packet. Loss uses only confirmed attempted probes, and reports local errors separately. Test integer millisecond values exactly as returned by the Windows API, including zero as below timer resolution.

## Offline integration

Start the actual Tkinter app without probing the network. Verify six tabs, responsive worker queue, invalid input, report export and safe close. Capture actual application screenshots and label the state as unmeasured. GUI screenshots are not live network evidence.

## Authorized real validation

Pending exact scope and permission. Record consent, interface/prefix, time, environment and command/application version privately. Verify selected subnet is within scope. Run a small discovery and 4-10 probes to an authorized target. Save raw per-probe outcomes, computed summary, actual screenshots and timestamped report. Verify counts and arithmetic independently. Repeat against an explicitly authorized nonresponding target only if available. Do not invent failed-host evidence.

## Artifacts and release

Preserve pytest stdout and JUnit XML in Evidence/mocked; GUI smoke logs/images in Evidence/offline; actual measurements only in Evidence/live. Do not substitute simulation for real testing. Validate PDF page counts (proposal 1-2, progress 2-3, report 8-12), fonts/spacing, all rendered pages, presentation 10-15 slides, ZIP CRC and root structure, no Documentation folder in ZIP, launch instructions from extracted source. Video is pending until a real recording exists.
