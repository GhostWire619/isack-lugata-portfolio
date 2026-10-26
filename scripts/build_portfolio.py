"""Regenerate the genuine-asset compositions and personalized captured pages."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
for script in ['build_identity_artwork.py','personalize.py','build_case_studies.py','build_seo.py','build_advertising.py','optimize_site.py']:
    subprocess.run([sys.executable,str(root/'scripts'/script)],cwd=root,check=True)
