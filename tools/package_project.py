"""Build the prescribed submission structure without private raw evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root/'CHUA_RALPH_MARTIN_FINALPROJECT.zip'
verification = root/'SourceCode/verification'
verification.mkdir(exist_ok=True)
for name in ['pytest-output.txt','pytest-results.xml','pytest-initial-collection-error.xml',
             'pytest-installed-environment.txt','pytest-installed-environment.xml','TEST_HISTORY.md']:
    shutil.copy2(root/'Evidence/mocked'/name, verification/name)
shutil.copy2(root/'Evidence/offline/gui-smoke.json', verification/'gui-smoke.json')
excluded = {'.venv','__pycache__','.pytest_cache','.git'}
files = []
for directory in ['SourceCode','Presentation','VideoDemo']:
    for file in sorted((root/directory).rglob('*')):
        if file.is_file() and not any(part in excluded for part in file.relative_to(root).parts):
            files.append(file)
files.append(root/'README.txt')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for directory in ['SourceCode','Presentation','VideoDemo']:
        z.writestr(directory+'/', b'')
    for file in files:
        z.write(file, file.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert {n.split('/')[0] for n in names} == {'SourceCode','Presentation','VideoDemo','README.txt'}
    assert not any('Documentation' in n or 'Evidence/live' in n or '.venv' in n for n in names)
    assert 'SourceCode/main.py' in names and 'Presentation/CCS234_Presentation.pptx' in names
    dest=root/'.build/extracted_submission'
    dest.mkdir(exist_ok=True)
    # Only our known relative file names are extracted; reject path traversal.
    for info in z.infolist():
        target=(dest/info.filename).resolve()
        if not target.is_relative_to(dest.resolve()):
            raise ValueError('Unsafe archive entry')
    z.extractall(dest)
manifest={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
result={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'zip_crc':'passed','required_structure':'passed','documentation_excluded':True,
        'raw_live_evidence_excluded':True,'file_count':len(files),'files':manifest,
        'video_status':'present' if (root/'VideoDemo/demonstration.mp4').exists() else 'PENDING - script and checklist only',
        'submission_ready':False,
        'remaining':['Real 5-10 minute formal-attire video','Institution page template','Individual/group authorship and filename approval','Personal review and final submission approval']}
(root/'PACKAGING_VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
