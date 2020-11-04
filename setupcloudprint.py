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
#    Copyright (C) 2011 Simon Cadman
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
from pip._vendor.msgpack.fallback import xrange


def printPrinters(printers):
    """Prints display name of printers.

    Formats as multiple columns if possible. Enumerates each printer name
    with integers starting with 1 (not zero).

    Args:
        printers: List of printers.

    Returns:
        number of printers printed
    """

    printer_names = \
        ["%d) %s" % (i + 1, printer['displayName']) for i, printer in enumerate(printers)]

    window_size = Utils.GetWindowSize()
    if window_size is None or window_size[0] > len(printer_names):
        for printer_name in printer_names:
            print(printer_name)
    else:
        window_width = window_size[1]
        max_name_length = max((len(printer_name) for printer_name in printer_names))
        # How many columns fit in the window, with one space between columns?
        column_quantity = max(1, (window_width + 1) / (max_name_length + 1))
        row_quantity = int(math.ceil(len(printer_names) / float(column_quantity)))

        for row_i in xrange(row_quantity):
            row_printers = []
            for printer_name in printer_names[row_i::row_quantity]:
                row_printers.append(printer_name.ljust(max_name_length))
            print(' '.join(row_printers))
    return len(printers)

if __name__ == '__main__':  # pragma: no cover
    import os
    import json
    import sys
    import math
    from auth import Auth
    from printermanager import PrinterManager
    from cupshelper import CUPSHelper
    from ccputils import Utils
    import argparse
    Utils.SetupLogging()

    # line below is replaced on commit
    CCPVersion = "20140814.2 000000"
    Utils.ShowVersion(CCPVersion)

    common_parser = argparse.ArgumentParser()
    common_parser.add_argument("--add-all", default="Y",
                               help="Add all printer from Google Account.")
    common_parser.add_argument("--prefix", default="GCP-",
                               help="Prefix printer name by.")
    common_parser.add_argument("--auto-clean", default="Y",
                               help="Remove deleted printer automatically")
    common_parser.add_argument("--user", default=None,
                               help="Use this account to map")
    common_parser.add_argument("--no-interactive", dest='interactive',
                               help="Don't ask any question ( by default )",
                               action='store_false')
    common_parser.add_argument("--interactive", dest='interactive',
                               help="Set interactive mode",
                               action='store_true')
    common_parser.add_argument("--gui", dest='gui',
                               help="Launch the browser",
                               action='store_true')
    common_parser.set_defaults(interactive=False)

    options = common_parser.parse_args(sys.argv[1:])
    if options.gui:
        Utils.GUI = True
    cupsHelper = None
    try:
        cupsHelper = CUPSHelper()
    except Exception as e:
        sys.stderr.write("Could not connect to CUPS: " + e.message + "\n")
        sys.exit(0)

    if os.path.exists(Auth.config):
        try:
            content_file = open(Auth.config, 'r')
            content = content_file.read()
            data = json.loads(content)
        except Exception:
            # remove old config file
            print("Deleting old configuration file: " + Auth.config)
            os.remove(Auth.config)

    while True:
        requestors, storage = Auth.SetupAuth(interactive=False)
        if storage is not False:
            print("You currently have these accounts configured: ")
            for requestor in requestors:
                print(requestor.getAccount())
            add_account = len(requestors) == 0
        else:
            add_account = True
        if not add_account:
            if not options.interactive:
                break
            answer = input("Add more accounts (Y/N)? ")
            if answer.lower().startswith("y"):
                add_account = True
            else:
                break
        if add_account:
            Auth.AddAccount(None, userid=options.user)

    for requestor in requestors:
        addedCount = 0
        cupsprinters = cupsHelper.getPrinters()
        prefix = ""
        printer_manager = PrinterManager(requestor)
        printers = printer_manager.getPrinters()
        if printers is None:
            print("Sorry, no printers were found on your Google Cloud Print account.")
            continue

        if options.add_all.lower() == "y":
            answer = "y"
        else:
            answer = input("Add all Google Cloud Print printers from %s to CUPS (Y/N)? " %
                               requestor.getAccount())

        if not answer.lower().startswith("y"):
            answer = 1
            print("Not adding printers automatically")

            while int(answer) != 0:
                maxprinterid = printPrinters(printers)
                answer = input("Add printer (1-%d, 0 to cancel)? " % maxprinterid)
                try:
                    answer = int(answer)
                except ValueError:
                    answer = 0
                if answer == 0:
                    continue
                if answer < 1 or answer > maxprinterid:
                    print("\nPrinter %d not found\n" % answer)
                    continue

                ccpprinter = printers[answer - 1]
                print("Adding " + printers[answer - 1]['displayName'])
                printername = options.prefix + \
                    str(ccpprinter.getDisplayName().encode('ascii', 'replace'), 'UTF-8')
                found = False
                for cupsprinter in cupsprinters:
                    if cupsprinters[cupsprinter]['device-uri'] == ccpprinter.getURI():
                        found = True
                if found:
                    print("\nPrinter with %s already exists\n" % printername)
                else:
                    printer_manager.addPrinter(printername, ccpprinter)

            continue

        for ccpprinter in printers:
            found = False
            for cupsprinter in cupsprinters:
                if cupsprinters[cupsprinter]['device-uri'] == ccpprinter.getURI():
                    found = True

            if found:
                continue

            printername = options.prefix + ccpprinter.getDisplayName()

            # check if printer name already exists
            foundbyname = False
            for ccpprinter2 in cupsprinters:
                printerinfo = cupsprinters[ccpprinter2]['printer-info']
                if printer_manager.sanitizePrinterName(printerinfo) == \
                        printer_manager.sanitizePrinterName(printername):
                    foundbyname = True
            if foundbyname:
                answer = input('Printer %s already exists, supply another name (Y/N)? ' %
                                   printer_manager.sanitizePrinterName(printername))
                if answer.startswith("Y") or answer.startswith("y"):
                    printername = input("New printer name? ")
                else:
                    answer = input("Overwrite %s with new printer (Y/N)? " %
                                       printer_manager.sanitizePrinterName(printername))
                    if answer.lower().startswith("n"):
                        printername = ""
            elif foundbyname:
                print("Not adding printer %s, as already exists" % printername)
                printername = ""

            if printername != "":
                printer_manager.addPrinter(printername, ccpprinter)
                cupsprinters = cupsHelper.getPrinters()
                addedCount += 1

        if addedCount > 0:
            print("Added %d new printers to CUPS" % addedCount)
        else:
            print("No new printers to add")

    printer_uris = []
    printer_manager = PrinterManager(requestors)
    printers = printer_manager.getPrinters()
    for printer in printers:
        printer_uris.append(printer.getURI())

    # check for printers to prune
    prunePrinters = []
    cupsprinters = cupsHelper.getPrinters()

    for cupsprinter in cupsprinters:
        if cupsprinters[cupsprinter]['device-uri'].startswith(Utils.PROTOCOL) \
                and cupsprinters[cupsprinter]['device-uri'] not in printer_uris:
            prunePrinters.append(cupsprinter)

    if len(prunePrinters) > 0:
        print("Found %d printers which no longer exist on cloud print:" % len(prunePrinters))
        for printer in prunePrinters:
            print(printer)
        if options.auto_clean.lower() == "y":
            answer = "y"
        else:
            answer = input("Remove (Y/N)? ")
        if answer.lower().startswith("y"):
            for printer in prunePrinters:
                cupsHelper.deletePrinter(printer)
                print("Deleted", printer)
        else:
            print("Not removing old printers")
