# Seven-minute demonstration script

Planned duration: approximately 7 minutes, including pauses and actual UI actions. Rehearse and verify the real recording stays between 5 and 10 minutes. Wear formal attire. This script is not a video.

## 0:00-0:40 Introduction

Introduce the presenter(s), CCS 234 and the Network Monitoring and Performance Analysis System. Explain that the application gathers a bounded connectivity sample from an authorized local network and produces a report. State that the tool does not certify network security or discover every active device.

## 0:40-1:20 Startup and scope

Launch main.py. Show the unmeasured Dashboard and six tabs. Refresh adapters. Explain that the IP and subnet come from the actual adapter netmask. Confirm the current network belongs to you or is authorized. Show the authorization control and four-packet limit. If the current network is not authorized, use the existing evidence while explicitly saying it is a saved measurement.

## 1:20-2:20 Network discovery

Start a bounded discovery only on the authorized local subnet. Explain that eight workers run probes while Tkinter remains responsive. Move between tabs while the scan runs. Show responding IP addresses and available hostnames. Explain why filtering and device isolation can hide active hosts. Avoid reading every private address aloud. Do not call every missing reply an offline device.

## 2:20-3:15 Connectivity and statistics

Select the router or another authorized target and run four probes if authorized for this rehearsal. Show each actual response time. Open Network Statistics and independently explain average, maximum and packet loss. For the saved October 27 capture, the router's genuine readings were 21, 8, 23 and 3 ms; average 13.75 ms, maximum 23 ms, 4/4 replies and 0% loss. This sequence is taken from the saved JSON evidence. New live values may differ: report what is actually on screen.

## 3:15-4:00 Recommendations and limitations

Open Security Recommendations. Explain the project thresholds: mean at least 100 ms or loss at least 20%. Show the general firewall and password reminders. Say explicitly that the application did not inspect passwords, vulnerabilities or firewall settings. Explain N/A for missing measurements and why local transport errors are excluded from the loss calculation.

## 4:00-5:00 Testing evidence

Run pytest in a terminal using the documented virtual-environment command. Explain that these deterministic tests mock the network and do not represent live performance. The verified baseline has 64 passing tests. Show examples for invalid input, timeouts, missing replies, arithmetic, scope restrictions and report export. Mention the first collection error and its import-path fix, preserved in the history. Only announce the new run's result after it finishes.

## 5:00-6:00 Reports and final output

Open Report Generator, save a timestamped TXT, JSON or PDF report, and inspect the saved file. Point out discovery results, per-probe values, statistics, rules and limitations. Explain that saved reports contain private local identifiers and should be reviewed before sharing. Show the report and presentation locations, with documentation outside the ZIP.

## 6:00-7:00 Conclusions and questions

Summarize which five features work and the limits of the evidence. The October 27 live scan tested 254 local candidates and received replies from 14 addresses; this is not a count of all installed devices. Describe future improvements such as IPv6 support and repeated authorized samples. State remaining submission steps: template verification, instructor agreement on authorship/filename and the completed recording. End with a clear view of the application and invite questions.
