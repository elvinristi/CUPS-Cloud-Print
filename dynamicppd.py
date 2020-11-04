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

import logging
import os
import urllib
import sys


def doList(sys, printer_manager):
    """Lists Google Cloud Print printers."""
    printers = printer_manager.getPrinters()
    if printers is None:
        sys.stderr.write("ERROR: No Printers Found\n")
        sys.exit(1)
    for printer in printers:
        print(printer.getCUPSDriverDescription())
    sys.exit(0)


def doCat():
    """Prints a PPD to stdout, per argv arguments."""
    try:
        drivername, accountName, printerId = sys.argv[2].split(':', 2)
        if drivername != 'cupscloudprint' or not printerId.endswith('.ppd'):
            raise Exception('Bad PPD name format')

        accountName = urllib.unquote(accountName)
        printerId = printerId[:-4]

    except Exception:
        sys.stderr.write("ERROR: PPD name '%s' is invalid\n" % sys.argv[2])
        sys.exit(1)

    printer = printer_manager.getPrinter(printerId, accountName)

    if printer is None:
        sys.stderr.write("ERROR: PPD %s not found\n" % sys.argv[2])
        sys.exit(1)

    print(printer.generatePPD())

    sys.exit(0)


def showUsage():
    sys.stderr.write("ERROR: Usage: %s [list|version|cat drivername]\n" % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':  # pragma: no cover

    libpath = "/usr/local/share/cloudprint-cups/"
    if not os.path.exists(libpath):
        libpath = "/usr/share/cloudprint-cups"
    sys.path.insert(0, libpath)

    from auth import Auth
    from printermanager import PrinterManager
    from ccputils import Utils

    if len(sys.argv) < 2:
        showUsage()

    Utils.SetupLogging()

    # line below is replaced on commit
    CCPVersion = "20140814.2 000000"
    Utils.ShowVersion(CCPVersion)

    requestors, storage = Auth.SetupAuth(False)
    if not requestors:
        sys.stderr.write("ERROR: config is invalid or missing\n")
        logging.error("backend tried to run with invalid config")
        sys.exit(1)

    printer_manager = PrinterManager(requestors)

    if sys.argv[1] == 'list':
        doList(sys, printer_manager)

    elif sys.argv[1] == 'cat':
        if len(sys.argv) == 2 or sys.argv[2] == "":
            showUsage()
        doCat()

    showUsage()
