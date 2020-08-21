
UNSUPPORTED
===========
CUPS Cloud Print is unsupported and has been for some time. Google Cloud Print itself will also be deprecated in December 2020 and you should migrate to an alternative. See [Google](https://support.google.com/chrome/a/answer/9633006) for more information.

[![Build Status](https://travis-ci.org/simoncadman/CUPS-Cloud-Print.png)](https://travis-ci.org/simoncadman/CUPS-Cloud-Print)
[![Coverage Status](https://coveralls.io/repos/simoncadman/CUPS-Cloud-Print/badge.png)](https://coveralls.io/r/simoncadman/CUPS-Cloud-Print)
[![Code Health](https://landscape.io/github/simoncadman/CUPS-Cloud-Print/master/landscape.png)](https://landscape.io/github/simoncadman/CUPS-Cloud-Print/master)

INTRODUCTION
============
Google Cloud Print driver for CUPS, allows printing to printers hosted on Google Cloud Print ( see http://www.google.com/cloudprint for more information ).

INSTALLATION
============

PACKAGE INSTALL ( Recommended )
================================

The recommended way to install CUPS Cloud Print is using your package manager, please see http://ccp.niftiestsoftware.com/ for installation 
instructions.

SOURCE INSTALL
==============

Clone the git repo:

git clone git://github.com/simoncadman/CUPS-Cloud-Print.git

cd CUPS-Cloud-Print/

./configure

make install

Follow configuration below.

CONFIGURATION
=============

Run /usr/share/cloudprint-cups/setupcloudprint.py ( or /usr/local/share/cloudprint-cups/setupcloudprint.py ) and either allow it to add all 
Cloud Print printers at once, or say 'N', and add manually:

Add a new printer ( via http://127.0.0.1:631 or usual interface ) as a 'Google Cloud Print' network printer. Select the 'Make' as Google, and 'Model' as Cloud Print.
Supply the connection name as a simple URI pointing to the printer you want to setup, you can obtain a list of URIs from 
/usr/share/cloudprint-cups/listcloudprinters.py ( or /usr/local/share/cloudprint-cups/listcloudprinters.py ) :
  
Print a test page, to confirm it is working.

Assuming the test page prints correctly, installation is complete.

DEVELOPING
==========

Before commiting to the git repository you should set up the pre-commit hook, this ensures the version numbers in the scripts are updated:

    ln -s ../../pre-commit.py .git/hooks/pre-commit

To run unit tests with a coverage report ( output into the htmlcov dir ) run this from within the CUPS Cloud Print directory:
    
    py.test -rfEsxw --cov . --cov-report html --ignore=oauth2client

Copyright and Trademark Information
===================================

Icon is licensed as Creative Commons - Attribution (CC BY 3.0) - http://creativecommons.org/licenses/by/3.0/us/, as are all original parts of the icon, which are combined to create the CUPS Cloud Print icon:
    
    - Cup icon ( http://thenounproject.com/term/cup/6566/ ) created by Monika Ciapala ( http://thenounproject.com/merdesign/ , http://www.merdesign.co.uk/ )
    
    - Cloud icon ( http://thenounproject.com/term/cloud/2788/ ) created by P.J. Onori ( http://thenounproject.com/somerandomdude/ , http://somerandomdude.com/ )
    
    - Printer icon ( http://thenounproject.com/term/printer/5043/ ) created by Dmitry Baranovskiy ( http://thenounproject.com/DmitryBaranovskiy/ , http://dmitry.baranovskiy.com/ )
    
    - Printer icon ( http://thenounproject.com/term/printer/5043/ ) created by Dmitry Baranovskiy ( http://thenounproject.com/DmitryBaranovskiy/ , http://dmitry.baranovskiy.com/ )
    
    - Arrow icon ( http://thenounproject.com/term/arrow/5449/ ) created by Jamison Wieser ( http://thenounproject.com/jamison/ , http://jamisonwieser.com/ )
    

Software copyright Simon Cadman and licenced under GNU GPL v3 ( http://www.gnu.org/licenses/gpl.html ).

Google is a trademark of Google Inc, and the software is unaffiliated with Google in any way.

CUPS and the CUPS logo are trademarks of Apple Inc. CUPS is copyright Apple Inc.
