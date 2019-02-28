#!"C:\Users\John Raymundo\PycharmProjects\FoundersClubEmailProject\venv\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'mail-parser==3.9.2','console_scripts','mailparser'
__requires__ = 'mail-parser==3.9.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('mail-parser==3.9.2', 'console_scripts', 'mailparser')()
    )
