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
import email.generator
import re
from auth import Auth
from urllib.parse import urlparse,unquote
from printer import Printer
from cupshelper import CUPSHelper
from ccputils import Utils


class PrinterManager(object):
    BOUNDARY = email.generator._make_boundary()
    CRLF = '\r\n'
    requestors = None
    cachedPrinterDetails = {}
    reservedCapabilityWords = {'Duplex', 'Resolution', 'Attribute', 'Choice', 'ColorDevice', 'ColorModel',
                               'ColorProfile', 'Copyright', 'CustomMedia', 'Cutter', 'Darkness', 'DriverType',
                               'FileName', 'Filter', 'Filter', 'Finishing', 'Font', 'Group', 'HWMargins', 'InputSlot',
                               'Installable', 'LocAttribute', 'ManualCopies', 'Manufacturer', 'MaxSize', 'MediaSize',
                               'MediaType', 'MinSize', 'ModelName', 'ModelNumber', 'Option', 'PCFileName',
                               'SimpleColorProfile', 'Throughput', 'UIConstraints', 'VariablePaperSize', 'Version',
                               'Color', 'Background', 'Stamp', 'DestinationColorProfile'}
    URIFormatLatest = 9999
    URIFormat20140308 = 3
    URIFormat20140307 = 2
    URIFormat20140210 = 1
    backendDescription =\
        'network %s "%s" "Google Cloud Print" "MFG:Google;MDL:Cloud Print;DES:GoogleCloudPrint;"'

    def __init__(self, requestors):
        """Create an instance of PrinterManager, with authorised requestor

        Args:
          requestors: list or CloudPrintRequestor instance, A list of
          requestors, or a single requestor to use for all Cloud Print
          requests.
        """
        self._cupsHelper = CUPSHelper()
        if requestors is not None:
            if isinstance(requestors, list):
                self.requestors = requestors
            else:
                self.requestors = [requestors]

    def getCUPSPrintersForAccount(self, account):
        cupsprinters = self._cupsHelper.getPrinters()
        accountPrinters = []
        for cupsprinter in cupsprinters:
            printer = self.getPrinterByURI(cupsprinters[cupsprinter]['device-uri'])
            if printer is not None:
                if printer.getAccount() == account:
                    accountPrinters.append(cupsprinters[cupsprinter])
        return accountPrinters

    def getPrinter(self, printerId, accountName):
        """Fetch one printer, including capabilities.

        Args:
          printerId: something like e64b1063-80e7-a87e-496c-3caa8cb7d736
          accountName: email address (account) printer is associated with

        Returns:
          A Printer object, or None if printer not found."""

        for requestor in self.requestors:
            if accountName != requestor.getAccount():
                continue

            response = requestor.printer(printerId)
            if response is None or not response['success'] \
                    or 'printers' not in response or not response['printers']:
                break

            return Printer(response['printers'][0], requestor, self._cupsHelper)

        return None

    def getPrinters(self, accountName=None):
        """Fetch a list of printers

        Returns:
          list: list of printers for the accounts.
        """
        if not hasattr(self, '_printers'):
            self._printers = []
            for requestor in self.requestors:
                if accountName is not None and accountName != requestor.getAccount():
                    continue

                responseobj = requestor.search()
                if 'printers' in responseobj:
                    for printer_info in responseobj['printers']:
                        self._printers.append(Printer(printer_info, requestor, self._cupsHelper))

        return self._printers

    def sanitizePrinterName(self, name):
        """Sanitizes printer name for CUPS

        Args:
          name: string, name of printer from Google Cloud Print

        Returns:
          string: CUPS-friendly name for the printer
        """
        name = name if isinstance(name, str) else str(name)
        name = str(name.encode('ascii', 'replace'), 'UTF-8').replace(' ', '_')

        return re.sub('[^a-zA-Z0-9\-_]', '', name)

    def addPrinter(self, printername, printer, location=None, ppd=None):
        """Adds a printer to CUPS

        Args:
          printername: string, name of the printer to add
          printer: Printer, CCP Printer object
          uri: string, uri of the Cloud Print device
          location: string, location of printer

        Returns:
          None
        """
        errorMessage = ""
        # fix printer name
        printername = self.sanitizePrinterName(printername)
        result = None
        printerppdname = None
        try:
            if ppd is None:
                printerppdname = printer.getPPDName()
            else:
                printerppdname = ppd
            if not location:
                location = printer.getLocation()
            if not location:
                location = 'Google Cloud Print'

            result = self._cupsHelper.addPrinter(
                printer, printername, location, printerppdname)
        except Exception as error:
            result = False
            errorMessage = error
        if result:
            print("Added " + printername)
            return True
        else:
            print("Error adding: " + printername, errorMessage)
            return False

    @staticmethod
    def _getAccountNameAndPrinterIdFromURI(uri):
        splituri = uri.rsplit('/', 2)
        accountName = unquote(splituri[1])
        printerId = unquote(splituri[2])
        return accountName, printerId

    def parseLegacyURI(self, uristring, requestors):
        """Parses previous CUPS Cloud Print URIs, only used for upgrades

        Args:
          uristring: string, uri of the Cloud Print device

        Returns:
          string: account name
          string: google cloud print printer name
          string: google cloud print printer id
          int: format id
        """
        formatId = None
        printerName = None
        accountName = None
        printerId = None
        uri = urlparse(uristring)
        pathparts = uri.path.strip('/').split('/')
        if uri.scheme == Utils.OLD_PROTOCOL_NAME:
            if len(pathparts) == 2:
                formatId = PrinterManager.URIFormat20140307
                printerId = unquote(pathparts[1])
                accountName = unquote(pathparts[0])
                printerName = unquote(uri.netloc)
            else:
                if unquote(uri.netloc) not in Auth.GetAccountNames(requestors):
                    formatId = PrinterManager.URIFormat20140210
                    printerName = unquote(uri.netloc)
                    accountName = unquote(pathparts[0])
                else:
                    formatId = PrinterManager.URIFormat20140308
                    printerId = unquote(pathparts[0])
                    printerName = None
                    accountName = unquote(uri.netloc)
        elif uri.scheme == Utils.PROTOCOL_NAME:
            formatId = PrinterManager.URIFormatLatest
            printerId = unquote(pathparts[0])
            printerName = None
            accountName = unquote(uri.netloc)

        return accountName, printerName, printerId, formatId

    def findRequestorForAccount(self, account):
        """Searches the requestors in the printer object for the requestor for a specific account

        Args:
          account: string, account name
        Return:
          requestor: Single requestor object for the account, or None if no account found
        """
        for requestor in self.requestors:
            if requestor.getAccount() == account:
                return requestor

    def getPrinterByURI(self, uri):
        accountName, printerId = self._getAccountNameAndPrinterIdFromURI(uri)
        return self.getPrinter(printerId, accountName)

    def getPrinterIDByDetails(self, account, printerid):
        """Gets printer id and requestor by printer

        Args:
          uri: string, printer uri
        Return:
          printer id: Single requestor object for the account, or None if no account found
          requestor: Single requestor object for the account
        """
        # find requestor based on account
        requestor = self.findRequestorForAccount(unquote(account))
        if requestor is None:
            return None, None

        if printerid is not None:
            return printerid, requestor
        else:
            return None, None
