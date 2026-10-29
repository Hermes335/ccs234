import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const runtime = 'C:/Users/Ralph/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES = `${runtime}/node/node_modules`;
process.env.RUNTIME_PYTHON = `${runtime}/python/python.exe`;
const { Presentation, PresentationFile } = await import(pathToFileURL(`${runtime}/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs`).href);
const skill = 'C:/Users/Ralph/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const {applyPresentationChartFont} = await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const root = process.cwd();
const build = path.join(root,'.build','slides');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(root,'Presentation'),{recursive:true});
const data = JSON.parse(await fs.readFile(path.join(root,'Evidence/live/network-report.json'),'utf8'));
const router = data.ping_runs[0];
const presentation = Presentation.create({slideSize:{width:1280,height:720}});
const C = {ink:'#142b43',muted:'#526679',accent:'#087e8b',white:'#ffffff'};
function text(slide,content,x,y,w,h,size=30,bold=false,color=C.ink){
  const s = slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  s.text=content;
  s.text.style={typeface:'Arial',fontSize:size,bold,color,verticalAlignment:'middle'};
  return s;
}
function base(title,notes){
  const slide=presentation.slides.add();slide.background.fill=C.white;
  text(slide,title,64,42,1152,98,44,true);
  text(slide,String(presentation.slides.items.length).padStart(2,'0'),1160,665,56,30,18,false,C.muted);
  slide.speakerNotes.text=notes;
  return slide;
}
function lines(slide,items,x=72,y=190,w=1100,size=30,gap=93){
  items.forEach((s,i)=>text(slide,s,x,y+i*gap,w,gap-12,size));
}
async function image(slide,file,x,y,w,h){
  const bytes=await fs.readFile(path.join(root,file));
  slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'Actual application screenshot; see speaker notes for provenance',fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
function node(slide,label,x,y,w,h){
  const s=slide.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'#f3f6f8',line:{fill:C.muted,width:1}});
  text(slide,label,x+12,y+10,w-24,h-20,27,true);
  return s;
}

let s=base('Network Monitoring and\nPerformance Analysis System', 'CCS 234 final project. Authors as supplied by the user. The briefs specify an individual project; instructor confirmation of group submission remains pending. Source: ALA CCS 234.pdf pp1-2; Final Project in CCS234 (2026).pdf pp1-6.');
text(s,'CCS 234 Communications and Networking',72,230,1100,60,30,false,C.accent);
text(s,'Ralph Martin Chua\nHerald Kent Amolong\nIvan Clyde Sagala',72,360,1000,150,30);
text(s,'Windows desktop application  /  27 October 2026',72,590,1000,40,24,false,C.muted);

s=base('The troubleshooting problem','Source: project proposal and supplied course briefs. These are project motivations, not results from a user survey.');
lines(s,['Separate command outputs make evidence difficult to compare.','A missing reply has several possible causes.','A useful diagnosis needs measured values, context and limits.']);

s=base('Project objectives','The five features are mandatory in Final Project in CCS234 (2026).pdf p2. Tkinter is optional in the PDF but required by the user.');
lines(s,['Identify responding addresses on an authorized local subnet.','Measure latency and packet loss with bounded ICMP tests.','Preserve results and explain connectivity recommendations.']);

s=base('Methodology','Sources: REQUIREMENTS.md, TEST_PLAN.md and Evidence folders. Mocked tests, offline UI checks and live measurements are distinct categories.');
lines(s,['Requirements and scope from both CCS 234 PDFs','Separated measurement, calculation and presentation code','Mocked pytest tests and actual GUI checks','Authorized live capture with retained original evidence'],72,175,1100,30,102);

s=base('System architecture','Editable architecture diagram. Source: SourceCode/netmonitor implementation. Workers exchange data through queue.Queue; only the main thread updates Tkinter. ICMP operates over IPv4; this does not measure TCP or UDP service availability.');
node(s,'Tkinter interface',420,165,440,80);
node(s,'Queue and service functions',350,315,580,80);
node(s,'Adapter metadata',60,510,340,88);
node(s,'Windows ICMP',470,510,340,88);
node(s,'Local reports',880,510,340,88);
for(const [x,y,w,h] of [[615,250,50,55],[195,425,50,60],[615,425,50,60],[1025,425,50,60]]){
  s.shapes.add({geometry:'downArrow',position:{left:x,top:y,width:w,height:h},fill:C.accent,line:{fill:'none',width:0}});
}

s=base('Five implemented features','Source: SourceCode/netmonitor modules; tests and live evidence. PDF export is implemented as an optional bonus. No port scanner or password audit is included.');
lines(s,['Discovery: actual adapter subnet and responding devices','Connectivity: selected targets and individual probe results','Statistics: mean, maximum and packet loss','Reports: timestamped TXT, JSON and PDF output','Recommendations: transparent rules and general advice'],72,165,1100,29,88);

s=base('Application demonstration','Actual screenshot Evidence/screenshots/01-startup-unmeasured.png. This is an unmeasured startup state. Demonstrate startup, adapter selection, permission, discovery, ping, statistics and export. The formal-attire video is not yet recorded.');
await image(s,'Evidence/screenshots/01-startup-unmeasured.png',64,165,775,490);
text(s,'Six views\n\nNo automatic scan\n\nExplicit scope\n\nBackground workers',880,220,320,370,29);

s=base('Authorized discovery results','Source: Evidence/live/network-report.json and summary.json, 2026-10-27 21:07:26-21:08:29 UTC+08:00. Home subnet detected from actual mask. 254 addresses x four probes. Fourteen responding addresses includes the laptop. No local API errors. Screenshot is actual GUI displaying recorded live results; it is not a new scan.');
await image(s,'Evidence/screenshots/02-discovery-recorded-live.png',64,165,775,490);
text(s,'14 responding\n254 candidates',880,210,320,150,40,true,C.accent);
text(s,'Four probes per target\n\nICMP can miss active devices',880,405,310,190,28);

s=base('Router latency sample','Source: Evidence/live/network-report.json, ping_runs[0]. Actual four samples are '+router.probes.map(p=>p.latency_ms).join(', ')+' ms. Router is 192.168.254.254. Reused discovery probes, no extra traffic. 55/4 = 13.75 ms, maximum 23 ms, 4/4 replies = 0% loss. Four probes do not establish long-term reliability.');
const chart=s.charts.add('bar',{position:{left:65,top:180,width:770,height:420},categories:['Probe 1','Probe 2','Probe 3','Probe 4'],series:[{name:'RTT in ms',values:router.probes.map(p=>p.latency_ms),fill:C.accent}],hasLegend:false,dataLabels:{showValue:true,position:'outEnd'},yAxis:{title:'Milliseconds',minimumScale:0,majorGridlines:{style:'solid',fill:'#dce3e9',width:1}}});
applyPresentationChartFont(chart,{fontFamily:'Arial'});
for (const style of [chart.dataLabels.textStyle,chart.xAxis.textStyle,chart.yAxis.textStyle]) { style.fontSize=22; }
chart.yAxis.title.textStyle.fontSize=22;
text(s,'13.75 ms mean\n23 ms maximum\n0% packet loss',880,225,335,230,34,true);
text(s,'One short sample\nFour replies from four attempts',880,500,325,100,24,false,C.muted);

s=base('Testing and error handling','Source: Evidence/mocked/pytest-output.txt and pytest-results.xml: 64 passed in 1.46 s. Initial collection failed with netmonitor import errors and was fixed with pythonpath configuration; preserved in TEST_HISTORY.md. Evidence/offline/gui-smoke.json: seven actual GUI checks using mocked data. Tests never scan a network.');
text(s,'64',72,170,300,170,120,true,C.accent);
text(s,'automated tests passed',72,350,650,70,36,true);
text(s,'Mocked network inputs\n\nSeven offline GUI checks\n\nSeparate live measurement evidence',760,180,440,300,30);
text(s,'Coverage: validation, timeouts, scope, cancellation, arithmetic, reports and rules',72,545,1100,85,28);

s=base('Recommendations and limits','Source: SourceCode/netmonitor/core.py recommendations. Loss >=20% and mean >=100 ms are project heuristics. General firewall/password advice does not establish security findings. Local transport errors are excluded from packet-loss denominators; unavailable measurements remain N/A.');
lines(s,['Alert thresholds: loss at least 20% or mean at least 100 ms','No reply can indicate filtering, isolation or unavailable hosts.','General firewall and password reminders accompany results.','No vulnerability, password or firewall configuration audit'],72,175,1100,29,105);

s=base('Conclusions and next steps','Sources: technical report Chapter 5 and PROJECT_STATUS.md. The implementation and measured validation are complete within scope. Remaining personal requirements: formal-attire video, page template, individual/group naming decision and final submission approval. No Teams submission has occurred.');
lines(s,['Five features work on the tested Windows laptop.','Short samples support troubleshooting, with explicit limits.','Remaining: real video, page template and authorship approval.','Future work: IPv6 and repeated authorized measurements.'],72,175,1100,30,105);

for(const [i,slide] of presentation.slides.items.entries()){
  const png=await presentation.export({slide,format:'png',scale:1});
  await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(root,'Presentation','CCS234_Presentation.pptx'),
  explicitTotalSlideCount:12,requiredNativeChartOwnerSlides:[9],requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,
  pythonExecutable:`${runtime}/python/python.exe`,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
  receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify(result));
