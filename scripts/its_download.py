#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import subprocess
import ConfigParser

from datetime import datetime
from datetime import timedelta


class DownloadResult:
	def __init__(self, code=None, errormsg=None, filename=None, cached=False):
		self._cached = cached
		self._filename = filename
		if errormsg:
			self._message = errormsg
		else:
			self._message = code
		self._success = filename or errormsg == 'There are no reports available to download for this selection.'
		if self._success or errormsg == 'Error :Your Apple ID or password was entered incorrectly.':
			self._retry = False
		elif errormsg == None or errormsg.startswith('Daily reports are available only for past '):
			self._retry = True
		else:
			self._retry = False
	
	def success(self):
		return self._success
	
	def retry(self):
		return self._retry
	
	def filename(self):
		return self._filename
	
	def message(self):
		return self._message
	
	def cached(self):
		return self._cached


class AppleServiceConnection:
	def __init__(self, username, password, vendor):
		self.username = username
		self.password = password
		self.vendor = vendor
	
	def download_report(self, typeofreport, datetype, reporttype, reportdate, destinationdir):
		result = None
		paramdict = {'USERNAME':self.username, 'PASSWORD':self.password, 'VNDNUMBER':self.vendor, 'TYPEOFREPORT':typeofreport, 'DATETYPE':datetype, 'REPORTTYPE':reporttype, 'REPORTDATE':reportdate}
		encoded_params = urllib.urlencode(paramdict)
		stream = urllib.urlopen('https://reportingitc.apple.com/autoingestion.tft?', encoded_params)
		code = stream.getcode()
		if code == 200:
			info = stream.info()
			wsfilename = info.getheader('filename')
			errormsg = info.getheader('ERRORMSG')
			if wsfilename:
				(discard, filename) = os.path.split(wsfilename)
				filepath = os.path.join(destinationdir, filename)
				if not os.path.exists(destinationdir):
					os.makedirs(destinationdir)
				f = open(filepath, 'wb')
				f.write(stream.read())
				f.close()
				result = DownloadResult(filename = filename)
			else:
				# Possible error messages:
				# 'Daily reports are available only for past 14 days, please enter a date within past 14 days.' (not available yet, retry)
				# 'There are no reports available to download for this selection.' (successfully got no report, don't retry)
				# 'Error :Your Apple ID or password was entered incorrectly.'
				print errormsg
				result = DownloadResult(errormsg = errormsg)
		else:
			print 'Return code = %d' % code
			result = DownloadResult(code = code)
		stream.close()
		return result
	
	def download_report_java(autoingestion_path, login, password, vendorid, destination):
		subprocess.check_call(['/usr/bin/java', '-classpath', autoingestion_path, 'Autoingestion', login, password, vendorid, 'Sales', 'Daily', 'Summary'])
	
	def download_daily_sales_report(self, report_date, destination_dir):
		return self.download_report('Sales', 'Daily', 'Summary', report_date, destination_dir)


class ReportDownloadCache:
	def __init__(self, apple_service, history_path):
		self.apple_service = apple_service
		self.history_path = history_path
	
	def format_date(self, report_date):
		return report_date.strftime('%Y%m%d')
	
	def get_report_date(self):
		report_date = datetime.utcnow() - timedelta(hours=37)
		report_date = report_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
		return report_date
	
	def get_daily_sales_report(self, destination_dir):
		formatted_report_date = self.format_date(self.get_report_date())
		history_filename = 'S_D_%s_history' % formatted_report_date
		history_filepath = os.path.join(self.history_path, history_filename)
		if os.path.exists(history_filepath):
			return DownloadResult(cached=True)
#			return DownloadResult(filename=xxx, cached=True)
		result = self.apple_service.download_daily_sales_report(formatted_report_date, destination_dir)
		if not result.retry():
			if not os.path.exists(self.history_path):
				os.makedirs(self.history_path)
			f = open(history_filepath, 'wb')
			if result.filename():
				f.write(result.filename())
			f.close()
		return result


class ReportDownloadManager:
	def __init__(self, config_path):
		parser = ConfigParser.SafeConfigParser()
		parser.read(config_path)
		username = parser.get('iTunes', 'username')
		password = parser.get('iTunes', 'password')
		vendor = parser.get('iTunes', 'vendor')
		history_path = parser.get('data', 'history')
		self.archive_path = parser.get('data', 'archive')
		self.apple_service = AppleServiceConnection(username, password, vendor)
		self.download_cache = ReportDownloadCache(self.apple_service, history_path)
	
	def get_reports(self):
		new_reports = {}
		result = self.download_cache.get_daily_sales_report(self.archive_path)
		if result.success() and result.filename():
			new_reports['daily_sales'] = result.filename()
		return new_reports
	
	def get_reports_for_date(self, report_date):
		new_reports = {}
		formatted_report_date = self.download_cache.format_date(report_date)
		result = self.apple_service.download_daily_sales_report(formatted_report_date, self.archive_path)
		if result.success() and result.filename():
			new_reports['daily_sales'] = result.filename()
		return new_reports


if __name__ == '__main__':
	show_usage = True
	if len(sys.argv) >= 2:
		config_path = sys.argv[1]
		show_usage = False
		report_manager = ReportDownloadManager(config_path)
		result = report_manager.get_reports()
		print result
	if show_usage:
		print 'Usage: its_download.py <config-file>'
