# Evidence provenance and privacy

- `mocked/`: pytest results. Synthetic fixtures, no network calls.
- `offline/`: actual GUI integration checks using explicitly mocked data.
- `live/`: genuine authorized home-network ICMP results and consent record. Four packets per candidate address. Router results reuse the discovery probes.
- `screenshots/`: actual application windows. Startup is unmeasured; subsequent screens display recorded live results. See PROVENANCE.txt.
- No simulated Packet Tracer measurements were used.

Private local addresses and hostnames remain in this local Evidence folder. The submission ZIP excludes raw live evidence. The technical report intentionally includes limited screenshots and the router sample to meet the evidence requirement; review these before sharing.
