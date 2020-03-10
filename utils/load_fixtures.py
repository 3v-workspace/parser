import re
import subprocess
import os
from os.path import isfile, join

path = "/app/docker_django/system/fixtures"
files = [filename for filename
         in os.listdir(path)
         if (isfile(join(path, filename))
             and re.match(r"^.*\.json$", filename))]

for file in files:
    filepath = os.path.join(path, file)
    try:
        subprocess.run(f"python manage.py loaddata {filepath}", shell=True)
    except Exception:
        pass