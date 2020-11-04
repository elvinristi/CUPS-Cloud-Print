#! /bin/sh
"true" '''\'
if command -v python2 > /dev/null; then
  exec python2 "$0" "$@"
else
  exec python "$0" "$@"
fi
exit $?
'''

#    CUPS Cloudprint - Print via Google Cloud Print
#    Copyright (C) 2013 Simon Cadman
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

if __name__ == '__main__':  # pragma: no cover

    import fileinput
    import re
    import sys
    import subprocess
    import os
    from datetime import datetime

    searchRegex = 'CCPVersion = "(\d)+ (\d){6}"'
    replaceValue = 'CCPVersion = "' + \
        datetime.utcnow().strftime('%Y%m%d %H%M%S') + '"'

    p = subprocess.Popen(
        ["git",
         "diff",
         "--cached",
         "--name-only"],
        stdout=subprocess.PIPE)
    output = p.communicate()[0]
    result = p.returncode
    if result != 0:
        sys.exit(result)
    alteredfiles = output.split("\n")
    for alteredfile in alteredfiles:
        if len(alteredfile) > 0 and os.path.exists(alteredfile) and alteredfile.endswith('.py'):
            p2 = subprocess.Popen(
                ["pep8",
                 "--max-line-length=100",
                 alteredfile],
                stdout=subprocess.PIPE)
            pep8output = p2.communicate()[0].strip()
            if p2.returncode != 0:
                print(alteredfile, "failed pep8 check:")
                print(pep8output)
            testfile = open(alteredfile, "r")
            fileNeedsUpdating = False
            for line in testfile:
                if '# line below is replaced on commit' in line:
                    fileNeedsUpdating = True
                    break
            testfile.close()

            if fileNeedsUpdating:
                replaceLine = False
                for line in fileinput.input(alteredfile, inplace=1):
                    if replaceLine:
                        line = re.sub(searchRegex, replaceValue, line)
                    if '# line below is replaced on commit' in line:
                        replaceLine = True
                    else:
                        replaceLine = False
                    sys.stdout.write(line)

                p = subprocess.Popen(
                    ["git",
                     "add",
                     alteredfile.lstrip('-')],
                    stdout=subprocess.PIPE)
                output = p.communicate()[0]
                result = p.returncode
                if result != 0:
                    sys.exit(result)
