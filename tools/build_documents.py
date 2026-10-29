"""Rebuild academic PDFs from source requirements and verified local evidence."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Ellipse
from reportlab.lib import colors

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'Documentation'
OUT.mkdir(exist_ok=True)
for name, filename in [('TNR','times.ttf'),('TNR-Bold','timesbd.ttf'),('TNR-Italic','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('TNR', normal='TNR', bold='TNR-Bold', italic='TNR-Italic', boldItalic='TNR-Bold')
BODY = ParagraphStyle('Body', fontName='TNR', fontSize=12, leading=24, alignment=TA_JUSTIFY, spaceAfter=8)
HEAD = ParagraphStyle('Heading', parent=BODY, fontName='TNR-Bold', alignment=TA_LEFT, spaceAfter=10)
CAP = ParagraphStyle('Caption', parent=BODY, fontName='TNR-Italic', spaceAfter=10)
LEFT = ParagraphStyle('Left', parent=BODY, alignment=TA_LEFT)
AUTHORS = 'Ralph Martin Chua; Herald Kent Amolong; Ivan Clyde Sagala'
live = json.loads((BASE/'Evidence/live/network-report.json').read_text(encoding='utf-8'))
summary = json.loads((BASE/'Evidence/live/summary.json').read_text(encoding='utf-8'))
router = live['ping_runs'][0]
samples = ', '.join(f"{p['latency_ms']:g}" for p in router['probes'])

def p(text, style=BODY):
    return Paragraph(text, style)

def heading(text):
    return p(text, HEAD)

def shot(name, width=468):
    return Image(str(BASE/'Evidence/screenshots'/name), width=width, height=width*780/1140)

def table(rows, widths):
    data = [[p(escape(str(cell)), LEFT) for cell in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#d9d9d9')),
                           ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),
                           ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                           ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    return t

def box(d,x,y,w,h,label):
    d.add(Rect(x,y,w,h,strokeColor=colors.black,fillColor=colors.white))
    for i,line in enumerate(label.split('\n')):
        d.add(String(x+w/2,y+h/2+6*(len(label.split('\n'))-1)-i*15,line,textAnchor='middle',fontName='TNR',fontSize=12))

def arrow(d,x1,y1,x2,y2):
    d.add(Line(x1,y1,x2,y2,strokeColor=colors.black))
    if y2 < y1:
        points=[x2,y2,x2-4,y2+7,x2+4,y2+7]
    else:
        points=[x2,y2,x2-7,y2-4,x2-7,y2+4]
    d.add(Polygon(points,fillColor=colors.black))

def architecture():
    d=Drawing(468,220)
    box(d,140,175,188,38,'Tkinter desktop GUI')
    box(d,125,105,218,42,'Queue and service functions')
    box(d,0,15,140,48,'Local adapter\nmetadata')
    box(d,164,15,140,48,'Windows ICMP\nauthorized subnet')
    box(d,328,15,140,48,'Local TXT JSON\nand PDF reports')
    arrow(d,234,175,234,147)
    for x in [70,234,398]:
        d.add(Line(234,105,x,83))
        arrow(d,x,83,x,63)
    return d

def flowchart():
    d=Drawing(468,225)
    box(d,3,165,145,45,'Select adapter\nand target')
    box(d,165,165,145,45,'Validate input\nand authorization')
    box(d,327,165,138,45,'Reject invalid\nor outside scope')
    arrow(d,148,188,165,188)
    arrow(d,310,188,327,188)
    d.add(String(314,215,'No',fontName='TNR',fontSize=12))
    box(d,165,85,145,45,'Worker runs at most\nfour probes per host')
    arrow(d,237,165,237,130)
    d.add(String(243,145,'Valid',fontName='TNR',fontSize=12))
    box(d,165,5,145,45,'Queue results\ncalculate and export')
    arrow(d,237,85,237,50)
    return d

def network_topology():
    d=Drawing(468,190)
    d.add(Rect(2,12,464,164,fillColor=None,strokeColor=colors.black))
    d.add(String(234,152,'Authorized home LAN 192.168.254.0/24',textAnchor='middle',fontName='TNR',fontSize=12))
    box(d,13,55,135,60,'Monitoring laptop\n192.168.254.118')
    box(d,167,55,135,60,'Wi-Fi router\n192.168.254.254')
    box(d,322,55,132,60,'Other authorized\nlocal addresses')
    arrow(d,148,86,167,86)
    arrow(d,302,86,322,86)
    d.add(String(234,29,'Bounded IPv4 ICMP echo over the local Wi-Fi network',textAnchor='middle',fontName='TNR',fontSize=12))
    return d

def usecases():
    d=Drawing(468,170)
    d.add(String(8,83,'Authorized user',fontName='TNR',fontSize=12))
    d.add(Rect(130,4,330,162,fillColor=None,strokeColor=colors.black))
    for i,label in enumerate(['View local network','Discover and test devices','Review statistics and advice','Save monitoring report']):
        y=141-i*38
        d.add(Ellipse(295,y,146,16,fillColor=colors.white,strokeColor=colors.black))
        d.add(String(295,y-4,label,textAnchor='middle',fontName='TNR',fontSize=12))
        d.add(Line(104,87,149,y,strokeColor=colors.black))
    return d

def footer(canvas, doc):
    canvas.setFont('TNR',12)
    canvas.drawString(72,36,'CCS 234 Communications and Networking')
    canvas.drawRightString(540,36,str(doc.page))

def build(name, pages):
    story=[]
    for index, page in enumerate(pages):
        if index:
            story.append(PageBreak())
        story.extend(page)
    SimpleDocTemplate(str(OUT/name), pagesize=(612,792), leftMargin=72,rightMargin=72,
                      topMargin=55,bottomMargin=60, title=name.replace('_',' ').replace('.pdf',''),
                      author=AUTHORS).build(story,onFirstPage=footer,onLaterPages=footer)

report=[
 [heading('Network Monitoring and Performance Analysis System'),
  p('Final Technical Report for CCS 234'), p(AUTHORS), p('West Visayas State University CICT<br/>27 October 2026'),
  heading('Chapter 1 Introduction'),
  p('Local connectivity problems are difficult to explain when troubleshooting depends on isolated commands and undocumented observations. A failed ping, for example, may reflect filtering or a route problem rather than a powered-off device. This project combines a bounded device discovery operation, individual connectivity measurements and a reproducible report in one Windows desktop application.'),
  heading('Problem Statement'),
  p('The project addresses the need to identify responding local addresses, measure latency and packet loss, and retain evidence without treating missing measurements as valid data. It follows the five required features in the final-project brief and the documentation structure in the ALA [1, 2].'),
  heading('Objectives'),
  p('The objectives are to discover responding devices on an authorized IPv4 subnet; perform at most four ICMP probes per target; calculate average latency, maximum latency and packet loss; generate local reports; and explain connectivity conditions using transparent recommendations. The Tkinter interface must remain responsive while network operations run.')],
 [heading('Chapter 2 System Design'), heading('Network Architecture'), network_topology(),
  p('Figure 1. Authorized local network topology. Other addresses represent scan candidates, not a verified inventory.',CAP),
  p('The application runs on the Windows laptop. The interface provider reads active adapter addresses and their actual masks. The user selects an authorized adapter; discovery is restricted to that subnet or a smaller portion. The implementation does not assume a default private-network prefix.'),
  p('ICMP echo requests operate over IPv4 and measure round-trip response time. They do not test application-level TCP or UDP services. Optional hostname resolution uses the operating system resolver. The operating system chooses the outgoing route; the selected adapter constrains destination scope but is not a forced source-interface binding.'),
  p('Workers return Python data objects through a queue. Only the main Tkinter thread updates widgets. Reports are written locally as text, JSON or PDF. No cloud database, notification service or packet inspection component is included. The implementation separates measurement transport from calculations so deterministic tests can replace the network boundary [3, 4].')],
 [heading('System Flowchart and Use Case Diagram'), flowchart(),
  p('Figure 2. Authorization and validation precede every network operation.',CAP), usecases(),
  p('Figure 3. The authorized user initiates each use case.',CAP),
  p('Cancellation prevents subsequent probes while allowing an in-flight request to finish within its timeout. Discovery records partial results as cancelled. A permission failure, invalid target or out-of-scope resolved address stops the operation and produces an error message. Starting the application does not send a probe.')],
 [heading('Chapter 3 Implementation'), heading('Tools Used'),
  p('The verified development environment used Windows and Python 3.10. Runtime components are Tkinter, psutil 7.2.2 and ReportLab 4.5.0. The automated suite used pytest 9.1.1. Visual Studio Code can open SourceCode as a normal Python project. The deliverable includes installation instructions and commented source; no proprietary development environment is required to run the application.'),
  heading('Source Code Description'),
  p('core.py defines validated probe records, ping sessions, arithmetic and rule-based advice. network.py reads interfaces, validates authorized scope, resolves names and uses the Windows IcmpSendEcho API. Each request has an 800 ms timeout in the interface. The API returns integer round-trip milliseconds, avoiding assumptions about the language of ping command output [3].'),
  p('reports.py creates a snapshot containing timestamps, provenance, detected devices, individual probes, statistics and limitations. It writes a temporary file and replaces the destination only after successful generation. gui.py implements the Dashboard, Network Discovery, Connectivity Testing, Network Statistics, Report Generator and Security Recommendations views.'),
  p('The interface captures input before creating a worker. Worker results enter a queue that Tkinter polls with after. Buttons prevent overlapping operations and cancellation uses a threading event. The automated tests replace transport and name resolution with deterministic fixtures, while the separate live capture uses the production Windows transport [4].')],
 [heading('Measurement and Recommendation Rules'),
  p('A reply contains a measured latency. A timeout or unreachable result has no latency. Local errors are kept separately because they may not confirm that a packet was sent. Empty data remains unavailable rather than being represented as zero. A Windows RTT of 0 ms is retained with a timer-resolution explanation.'),
  heading('Calculation Definitions'),
  p('Average latency is the sum of reply latencies divided by the number of replies. Maximum latency is the largest reply latency. Both are unavailable when there are no replies. Packet loss is 100 multiplied by the difference between confirmed attempts and replies, divided by confirmed attempts. No confirmed attempts produces an unavailable percentage.'),
  p('For this project, confirmed attempts include reply, timeout and ICMP unreachable outcomes. Other local API errors are excluded and counted explicitly. Discovery performs four probes per candidate, with at most eight targets processed concurrently and a maximum subnet size of 256 addresses. Larger adapter networks require selection of a smaller authorized subnet.'),
  heading('Transparent Security Recommendations'),
  p('Loss of at least 20% or average latency of at least 100 ms triggers an alert. These thresholds are project heuristics and are not universal performance standards. The application also explains the ambiguity of no echo reply and provides general firewall and password reminders. It does not inspect credentials, firewall configuration or vulnerabilities and therefore makes no security certification.')],
 [heading('Chapter 4 Results and Testing'), heading('Evidence Collection Method'),
  p('The user explicitly confirmed the connected home Wi-Fi and authorized local ICMP discovery. Windows classified the connection as Public; testing waited for the user to confirm ownership rather than treating that profile as authorization. The adapter supplied 192.168.254.118 with mask 255.255.255.0, giving 192.168.254.0/24.'),
  shot('01-startup-unmeasured.png',400),
  p('Figure 4. Actual unmeasured application startup. No network operation runs automatically.',CAP),
  p('The live scan ran on 27 October 2026 from 21:07:26 to 21:08:29 at UTC+08:00. Raw JSON, text and PDF reports are stored in Evidence/live. Screenshots on the following pages show the actual application displaying that saved live capture. No extra probes were sent to create the screenshots.')],
 [heading('Discovery Results and Interpretation'), shot('02-discovery-recorded-live.png',468),
  p('Figure 5. Actual application view of recorded live discovery results.',CAP),
  p('The operation tested 254 candidate addresses and received at least one echo reply from 14 addresses. Every candidate had four bounded probes and the capture recorded no local API errors. The 14 responding addresses include the monitoring laptop; they must not be described as 14 additional physical devices.'),
  p('The remaining addresses did not return successful echo replies during the sample. This does not prove that they were unused or offline. ICMP policy, wireless isolation and transient loss can affect discovery. The result is therefore a count of responding addresses at one point in time, not a complete inventory. Hostnames appear only when resolution succeeded.')],
 [heading('Router Performance Evaluation'), shot('03-statistics-recorded-live.png',430),
  p('Figure 6. Actual statistics screen displaying saved router measurements.',CAP),
  p(f'The router at {router["ip"]} returned four replies. The recorded round-trip samples were {samples} ms. Their sum is 55 ms, giving 55 / 4 = 13.75 ms average latency. The maximum is 23 ms. Four replies from four attempts gives (4 - 4) / 4 x 100 = 0% packet loss.'),
  p('The router did not trigger the configured loss or mean-latency alerts in this sample. Four replies do not establish long-term stability, Internet performance or application throughput. The report reuses the router probes from discovery instead of issuing another set. Results are genuine observations from the authorized home network, distinct from mocked test fixtures.')],
 [heading('Verified Automated and Offline Testing'),
  table([['Evidence category','Verified result'],['Mocked automated tests','64 passed in 1.46 seconds'],['Offline GUI integration','7 checks passed without network access'],['Live discovery','254 candidates; 14 responding addresses'],['Router sample','4 replies; 13.75 ms mean; 23 ms max; 0% loss']], [195,273]),
  p('The pytest suite covers target and scope validation, bounded counts and timeouts, successful and failed probes, resolution failure, cancellation, arithmetic, missing measurements, report export and recommendation rules. It replaces network calls and makes no claim about live performance.'),
  p('The first execution failed during collection because the project package was not on the import path when pytest ran from the workspace root. No test bodies ran in that attempt. Adding pythonpath = . to the pytest configuration resolved the cause; the rerun executed all 64 tests successfully. Both the initial JUnit failure record and the successful log are retained.'),
  p('The offline integration check exercised the real Tkinter widgets, six tabs, initial unmeasured state, queue-driven result rendering, mocked provenance, recommendation display and cleared state. Visual inspection exposed a footer layout issue; the layout was corrected and the screenshots were recaptured. This is narrower than a complete independent user acceptance study.')],
 [heading('Chapter 5 Conclusions and Recommendations'),
  p('The application implements the five required features and the Tkinter interface. Deterministic tests verify core calculations and error handling, while the authorized home-network capture verifies that the production Windows transport can discover responding addresses and record genuine measurements. Local text, JSON and PDF report generation provides a reproducible record.'),
  p('The evidence supports a working IPv4 monitoring prototype on the tested Windows laptop. It does not establish completeness of discovery, long-term reliability, throughput or security posture. Recommended improvements include IPv6 support, configurable repeated authorized sampling and clearer comparisons across measurement sessions. These remain future work rather than implemented features.'),
  heading('Remaining Submission Requirements'),
  p('The formal-attire demonstration video has not been recorded. The provided script and checklist must be used to produce and review a real five-to-ten-minute recording. The institution page template referenced in the ALA was not supplied; this report uses Times New Roman at 12 points, double-spaced justified body text with provisional one-inch side margins.'),
  p('The supplied author names identify three people, although both briefs describe an individual project. Instructor approval of that arrangement and the final archive filename remains necessary. The ALA ends the project period on December 5 while the final brief names December 4 as the submission date; plan for the earlier date until clarified. No Teams submission has been performed.')],
 [heading('References'),
  p('[1] West Visayas State University CICT. ALA for Finals, CCS 234 Communications and Networking. User-supplied file ALA CCS 234.pdf, 2026, pages 1-2.'),
  p('[2] West Visayas State University CICT. Network Monitoring and Performance Analysis System, Final Project. User-supplied file Final Project in CCS234 (2026).pdf, 2026, pages 1-6.'),
  p('[3] Microsoft Learn. IcmpSendEcho function and ICMP_ECHO_REPLY structure. Accessed 27 October 2026. <link href="https://learn.microsoft.com/en-us/windows/win32/api/icmpapi/nf-icmpapi-icmpsendecho">IcmpSendEcho API documentation</link> and <link href="https://learn.microsoft.com/en-us/windows/win32/api/ipexport/ns-ipexport-icmp_echo_reply">ICMP_ECHO_REPLY structure documentation</link>.'),
  p('[4] Python Software Foundation. Python documentation: queue and tkinter modules. Accessed 27 October 2026. <link href="https://docs.python.org/3/library/queue.html">https://docs.python.org/3/library/queue.html</link> and <link href="https://docs.python.org/3/library/tkinter.html">https://docs.python.org/3/library/tkinter.html</link>.'),
  heading('Local Verification Records'),
  p('SourceCode contains the implementation and automated tests. Evidence/mocked contains pytest-output.txt, pytest-results.xml and the initial collection-failure record. Evidence/offline contains gui-smoke.json. Evidence/live contains authorization.json, network-report.json and summary.json. Evidence/screenshots contains the original application captures and their provenance note.'),
  p('These local records are primary project evidence. Private raw network data is excluded from the submission archive. Review the limited addresses and hostnames visible in this report before sharing it with the instructor.')]
]
build('Final_Technical_Report.pdf',report)

proposal=[
 [heading('CCS 234 Project Proposal'), heading('Network Monitoring and Performance Analysis System'),p(AUTHORS),
  p('Prepared 27 October 2026 for the Week 14 proposal requirement. This document states the project plan; the technical report records completed testing separately.'),
  heading('Problem Statement'),
  p('Students and home-network users need a small tool that combines local device discovery, bounded connectivity testing and interpretable results. Separate command outputs make it difficult to preserve a consistent timestamped record. Missing responses are also easy to misinterpret as proof that a device is offline.'),
  heading('Objectives'),
  p('The proposed system will detect the actual local IPv4 address and subnet, identify responding authorized addresses, perform up to four ICMP probes per target, calculate mean and maximum latency and packet loss, save local reports, and provide transparent connectivity recommendations. A Tkinter interface will keep network work separate from widget updates.'),
  heading('Scope'),
  p('The initial scope is a Windows laptop on an explicitly authorized home or laboratory IPv4 subnet. Discovery will be bounded to at most 256 addresses. Intrusive scanning, password testing, exploitation, packet capture and external-network scanning are excluded. Hostname availability and ICMP filtering will be reported as limitations.')],
 [heading('Methodology and Expected Output'),
  p('Development proceeds through requirements analysis, separated network and calculation modules, a six-view desktop interface, deterministic automated tests, authorized live validation, and preparation of the required documentation and presentation. The two supplied CCS 234 PDFs control the deliverables and rubric.'),
  heading('Tools and Technologies'),
  p('Python and Tkinter provide the desktop application. psutil reads adapter metadata and the Windows ICMP API supplies bounded echo requests. ReportLab supports optional PDF export. pytest tests pure logic and injected transport behavior. Visual Studio Code serves as an editor without becoming a runtime dependency.'),
  heading('Verification Plan'),
  p('Mocked tests cover valid and invalid targets, timeouts, unreachable outcomes, numerical calculations, report output and recommendation thresholds. Live measurements require explicit network permission and will be labeled separately. Genuine screenshots and retained test logs will support the results chapter; unavailable evidence will be reported honestly.'),
  heading('Expected Deliverables and Schedule'),
  p('Expected outputs are commented source, installation instructions, a one-to-two-page proposal, a two-to-three-page progress report, an eight-to-twelve-page technical report, ten-to-fifteen presentation slides and a five-to-ten-minute formal-attire demonstration. The brief specifies progress on November 17, final submission on December 4 and presentations on December 8-10, 2026. Template availability, the ALA date conflict and individual-versus-group authorship require instructor clarification.')]
]
build('Project_Proposal.pdf',proposal)

progress=[
 [heading('CCS 234 Progress Report'),p(AUTHORS),p('Status as of 27 October 2026. Prepared in advance of the Week 15 milestone.'),
  heading('System Design and Accomplishments'),architecture(),
  p('The five required modules and six Tkinter views are implemented. The design separates OS calls from statistics, recommendation rules and file output. Network work executes in background workers, and a queue returns results to the main GUI thread. Discovery uses the actual adapter subnet, checks authorization and limits requests to four per candidate.'),
  p('The automated suite executed 64 tests successfully after fixing an initial package-import collection error. An offline GUI integration check passed seven checks. Authorized live validation tested 254 addresses, with 14 returning echo replies. Raw records are stored separately from mocked test evidence.')],
 [heading('Actual Application Screenshot'),shot('03-statistics-recorded-live.png',468),
  p('The actual application displays saved genuine measurements from the authorized home-network capture. This screenshot is a replay of recorded results, not a new live test.',CAP),
  p('The router returned four responses with latencies of '+samples+' ms. The mean was 13.75 ms, the maximum was 23 ms and packet loss was 0%. These values describe only the bounded sample. ICMP discovery does not guarantee a complete inventory and does not measure application throughput or vulnerability exposure.')],
 [heading('Sample Code and Remaining Tasks'),
  p('The following excerpt from core.py selects measured reply latencies and counts outcomes whose send attempt is not classified as a local error. It is actual implementation code.'),
  p('replies = [p.latency_ms for p in probes<br/>&nbsp;&nbsp;&nbsp;&nbsp;if p.status == "reply"]<br/>attempted = sum(p.status != "error" for p in probes)',LEFT),
  p('The statistics function returns unavailable latency when no replies exist. Packet loss excludes local errors with unknown send status. The rule module reports configured thresholds explicitly and separates connectivity findings from general firewall and password reminders.'),
  heading('Remaining Tasks'),
  p('The presenters must record and review the real formal-attire video. The referenced institutional page template must be obtained or the provisional formatting accepted by the instructor. The three supplied names must be reconciled with the individual-project instruction and final archive naming convention. The course deadline conflict also needs clarification.'),
  p('Before submission, the student must review private information in screenshots and reports, verify the installation on the demonstration machine, and approve the final package. The technical documentation remains outside the ZIP, and no Teams submission has been made. Future technical work may add IPv6 and repeated sampling after the current required scope is accepted.')]
]
build('Progress_Report.pdf',progress)
(OUT/'DOCUMENTATION_NOTES.md').write_text('Academic PDFs use embedded Times New Roman 12 pt, 24 pt line leading, justified body text and bold/italic emphasis. Page size is Letter with provisional one-inch side margins. Institution template not supplied. Original evidence remains in ../Evidence. Three authors are listed as supplied; individual/group and archive naming need instructor confirmation. No video exists yet.\n', encoding='utf-8')
print('Generated technical report, proposal and progress report.')
