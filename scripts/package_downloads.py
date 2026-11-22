"""Refresh the static site's download bundles. Run from any directory."""
from pathlib import Path
import shutil,zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'site/downloads';OUT.mkdir(exist_ok=True)
shutil.copy2(ROOT/'LICENSE',OUT/'LICENSE.txt')
# Keep the website's Russian guide separate from the English repository guide.
shutil.copy2(ROOT/'site/solar-car-assets/panel-assembly.ru.pdf',OUT/'solar-car-assembly.pdf')
for extension,folder in [('stl','print'),('step','step')]:
    with zipfile.ZipFile(OUT/f'solar-car-{extension}.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted((ROOT/'models'/folder).glob('*.'+extension)):archive.write(p,p.name)
with zipfile.ZipFile(OUT/'solar-car-source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in rel.parts for x in ['.git','.cache','__pycache__','.venv','venv','build','downloads']):continue
        if p.name.startswith('.env') or p.suffix in ['.key','.pem']:continue
        archive.write(p,Path('solar-car')/rel)
for p in OUT.glob('*.zip'):
    with zipfile.ZipFile(p) as archive:assert archive.testzip() is None
print('Download bundles refreshed')
