# CCS 234 requirements and traceability

Reviewed 2026-10-27: all 2 pages of `ALA CCS 234.pdf` (ALA) and all 6 pages of `Final Project in CCS234 (2026).pdf` (FP). These supplied PDFs control course requirements; the user's request adds reliability, testing and evidence constraints.

## Mandatory application requirements

| ID | Requirement | Source | Planned implementation and verification |
|---|---|---|---|
| F1 | Detect local IP, display network range, list active devices | FP p2 | Interface selection with actual netmask; bounded authorized IPv4 discovery; mocked discovery tests and pending live validation |
| F2 | Ping selected devices, response time, packet loss | FP p2 | Target validation, bounded ICMP probes, per-probe results; success, failure and timeout tests |
| F3 | Hostname, IP, average/max latency, packet loss | FP p2 | Per-run statistics; missing values remain unavailable; arithmetic and no-response tests |
| F4 | Timestamp, detected devices, ping results, performance summary | FP p2 | Local text/JSON reports, optional PDF; report content and save tests |
| F5 | Weak connectivity, unreachable hosts, firewall and password advice | FP p2 | Documented rule thresholds, general advice without claiming a security audit; rule tests |

User additions: Tkinter GUI is mandatory for this implementation; background operations must not touch widgets; target hostnames where available; invalid input/error handling; pytest; honest evidence with mocked/simulated/live categories; no network scan without authorization.

## Optional bonuses

FP p2 lists Tkinter GUI, dashboard charts, PDF export, email notification, port scanner, Wireshark packet integration, real-time monitoring and cloud database storage. Prioritize GUI and PDF export. Other bonuses are outside the initial scope. Wireshark is a course topic/tool (FP p1), but packet integration is explicitly optional (p2).

## Deliverables

- Proposal, Week 14, 1-2 pages: title, problem, objectives, methodology, tools, expected output (FP p3).
- Progress report, Week 15, 2-3 pages: design, actual screenshots, sample code, accomplishments, remaining tasks (FP p3).
- Technical report, 8-12 pages (FP p3): Chapter 1 introduction/background/problem/objectives; Chapter 2 architecture/flowchart/use-case diagram; Chapter 3 tools/source description; Chapter 4 screenshots/performance evaluation; Chapter 5 conclusions/recommendations; references.
- ALA p1: Times New Roman 12 pt, fully justified, double spaced; only bold, italic and underline for emphasis; use attached page template.
- Commented source, README, installation instructions (FP p4).
- Presentation: 10-15 slides covering title, overview, problem, objectives, methodology, architecture, features, demonstration, results, conclusion (ALA p1, FP p4).
- Video: 5-10 minutes in formal attire, showing startup, features, testing results, final output (ALA p1, FP p4). A script is preparation, not a recorded video.
- Archive `LASTNAME_FIRSTNAME_FINALPROJECT.zip` contains `SourceCode/`, `Presentation/`, `VideoDemo/`, `README.txt`. Documentation is excluded and submitted separately via Teams (ALA p2, FP p6). No Teams submission authorized.

## Testing and evaluation

PDFs require screenshots and performance evaluation, testing evidence and analysis (10 grading points), and testing results in the video. They do not prescribe pytest or a test count. The user additionally requires automated discovery/connectivity/validation/timeout/statistics/report/security/error tests, meaningful preserved logs, genuine screenshots and measurements, and explicit outstanding manual validation when live access is unavailable.

## Grading

| Criterion | Points |
|---|---:|
| Functionality | 30 |
| Technical implementation | 20 |
| UI and design | 10 |
| Documentation | 15 |
| Testing and evaluation | 10 |
| Presentation and demonstration | 10 |
| Innovation and creativity | 5 |
| Total | 100 |

Functionality levels: excellent 27-30, very good 23-26, good 19-22, fair 15-18, poor 0-14. Technical levels: excellent 18-20, very good 15-17, good 12-14, fair 8-11, poor 0-7 (ALA p2, FP p5). Overall ratings: excellent 90-100%, very good 80-89%, good 70-79%, fair 60-69%, poor below 60% (FP p5). No grade is predicted by this project.

## Conflicts, unknowns and decisions

1. ALA project duration is October 29-December 5, 2026. FP p4 specifies progress November 17, final submission December 4, presentation December 8-10. Plan for December 4; instructor must resolve dates. Work began October 27 at the user's request.
2. The ALA references an attached page template, but neither supplied PDF contains a blank template and no separate template was found. Use conservative academic formatting provisionally and mark template compliance pending.
3. ZIP list mentions Documentation but explicitly excludes it. Follow the exclusion, keep documentation adjacent to the archive.
4. GUI is optional in FP but expressly required by the user; implement it.
5. Initially missing identity and testing scope were requested. The user supplied Ralph Martin Chua, Herald Kent Amolong and Ivan Clyde Sagala, and explicitly authorized bounded discovery on the detected home subnet after confirming the connected Wi-Fi. List all three authors; the individual-project requirement and final archive naming still need instructor confirmation. The archive provisionally uses the first supplied author's name.
6. No loss/latency thresholds are specified. Adopt clearly labeled project heuristics (loss >=20%, mean latency >=100 ms) rather than claiming universal standards.
7. Device discovery cannot prove completeness; ICMP filtering and isolated clients can hide active hosts. No reply is not proof that a machine is powered off.

Phase 1 extraction is complete. The missing template, identity, schedule clarification and network authorization do not block offline implementation.
