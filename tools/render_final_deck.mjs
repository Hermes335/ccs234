import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from 'file:///C:/Users/Ralph/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const presentation=await PresentationFile.importPptx(await FileBlob.load('Presentation/CCS234_Presentation.pptx'));
await fs.mkdir('.build/final_slide_previews',{recursive:true});
for(const [i,slide] of presentation.slides.items.entries()){
  const png=await presentation.export({slide,format:'png',scale:1});
  await fs.writeFile(`.build/final_slide_previews/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
}
console.log('Rendered all '+presentation.slides.items.length+' slides from the final exported PPTX.');
