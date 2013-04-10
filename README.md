iTunesStats
===========

This set of Python scripts allows to:

 - collect daily sales data from iTunes Connect,
 - store sales information into a sqlite database,
 - generate reports from this data.

Requirements:

 - Python 2.7: <http://www.python.org>
 - SQLite 3: <http://www.sqlite.org>
 - Mako: <http://www.makotemplates.org/>
 - Flotr2: <http://humblesoftware.com/flotr2/>


Installation
============

The "scripts" and "templates" folders may be installed in any location.
In order to invoke the iTunesStats command without providing its full path, it is possible to either add the "scripts" folder to your $PATH, or create a symlink to iTunesStats from any location in your $PATH (typically /usr/local/bin).

The "Flotr2" folder must be installed in a location published by your web server (on Mac OS X: inside /Library/WebServer/Documents).


Configuration Files
===================

In order to simplify the command line, and to prevent sensitive data from being exposed during execution, iTunesStats actions take their parameters from configuration files. These files are in the well-known ".ini" format, and may include up to 3 sections.

 - the `[iTunes]` section contains your credentials on iTunes Connect (username, password and vendor identifier). It is used by the download and download-import actions.
 - the `[data]` section defines the SQLite file to be used as your data store (database), as well as the folders used to store the txt.gz archive files (archive), and an internal folder used to keep track of the requests sent to the iTunes service (history). This section is used by all actions.
 - the `[report]` section defines the path to the "templates" directory, and the path to the directory where the generated files will be sent (typically the folder where you installed Flotr2 previously). This section is used by the report action.


Usage
=====

Supported options:

 - `--download CONFIG_FILE`: download daily summary from iTunes Connect into txt.gz archive file
 - `--download-import CONFIG_FILE`: download daily summary from iTunes Connect into archive file and database
 - `--date REPORT_DATE`: download report for the specified date (by default: yesterday) (this option can be used with --download or --download-import)
 - `--import CONFIG_FILE PATH`: import txt.gz archive file(s) into database
 - `--report CONFIG_FILE`: generate html report

The download, download-import, import and report actions can be performed in the same command, even multiple times, with different configuration files.


Examples
========

Simple case: one developer account, one database, one report
------------------------------------------------------------

__/Library/iTunesSales/simple/simple.config__

	[iTunes]
	username = account@example.com
	password = password1234
	vendor = 87654321

	[data]
	archive = /Library/iTunesSales/simple/archive
	history = /Library/iTunesSales/simple/history
	database = /Library/iTunesSales/simple/sales.db

	[report]
	templates = /Library/iTunesSales/templates
	output = /Library/WebServer/Documents/simple-report

__Daily script:__

	iTunesStats --download-import /Library/iTunesSales/simple/simple.config --report /Library/iTunesSales/simple/simple.config

Merging sales from two developer accounts into a single report
--------------------------------------------------------------

__/Library/iTunesSales/merge/acct1.config__

	[iTunes]
	username = account1@example.com
	password = password1
	vendor = 88881111

	[data]
	archive = /Library/iTunesSales/merge/archive
	history = /Library/iTunesSales/merge/history
	database = /Library/iTunesSales/merge/sales.db

__/Library/iTunesSales/merge/acct2.config__

	[iTunes]
	username = account2@example.com
	password = password2
	vendor = 88882222

	[data]
	archive = /Library/iTunesSales/merge/archive
	history = /Library/iTunesSales/merge/history
	database = /Library/iTunesSales/merge/sales.db

__/Library/iTunesSales/merge/report.config__

	[data]
	database = /Library/iTunesSales/merge/sales.db

	[report]
	templates = /Library/iTunesSales/templates
	output = /Library/WebServer/Documents/merge-report

__Daily script:__

	iTunesStats --download-import /Library/iTunesSales/merge/acct1.config --download-import /Library/iTunesSales/merge/acct2.config --report /Library/iTunesSales/merge/report.config


License
=======

By Frank Lefebvre (@franklefebvre) & Jacques Foucry (@jfoucry)

This software is distributed under the BSD License.
