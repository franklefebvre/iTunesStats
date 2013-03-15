#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import glob
import gzip
import os
import sys

import its_database


class DailySummaryFileReader:
	def __init__(self):
		self.daily_summary_headers = [
			"Provider",
			"Provider Country",
			"SKU",
			"Developer",
			"Title",
			"Version",
			"Product Type Identifier",
			"Units",
			"Developer Proceeds",
			"Begin Date",
			"End Date",
			"Customer Currency",
			"Country Code",
			"Currency of Proceeds",
			"Apple Identifier",
			"Customer Price",
			"Promo Code",
			"Parent Identifier",
			"Subscription",
			"Period"
		]
		self.daily_summary_fields = [
			"provider",
			"provider_country",
			"product_sku",
			"developer",
			"product_name",
			"product_version",
			"transaction_type",
			"units",
			"payment_price",
			"begin_date",
			"end_date",
			"customer_currency",
			"customer_country",
			"payment_currency",
			"apple_product_id",
			"customer_price",
			"promo_code",
			"iap_parent_sku",
			"subscription_type",
			"subscription_period"
		]
	
	def validate_header(self, line):
		elements = line.strip().split('\t')
		return elements == self.daily_summary_headers
	
	def decode_row(self, line):
		elements = line.strip().split('\t') + [None]*len(self.daily_summary_fields)
		row_dict = {self.daily_summary_fields[i] : elements[i] for i in range(len(self.daily_summary_fields))}
		if row_dict['begin_date'] != row_dict['end_date']:
			return None
		if row_dict['provider'] != 'APPLE':
			return None
		if row_dict['provider_country'] != 'US':
			return None
		row_dict['date'] = datetime.strptime(row_dict['begin_date'], '%m/%d/%Y')
		return row_dict
	
	def read_lambda(self, filename, lf):
		success = False
		f = gzip.open(filename, 'rb')
		if self.validate_header(f.readline()):
			success = True
			for line in f:
				row_dict = self.decode_row(line.decode('utf-8'))
				if row_dict:
					lf(row_dict)
				else:
					print 'Invalid row in file %s' % filename
					success = False
					break
		else:
			print 'Invalid header in file %s' % filename
		f.close()
		return success
		
	def read(self, filename):
		rows = []
		if not self.read_lambda(filename, lambda row: rows.append(row)):
			rows = None
		return rows


def import_into_database(db, row):
	date_id = db.select_date(row['date'])
	if date_id == None:
		date_id = db.insert_row_dict('report_date', ['date'], row)
	product_id = db.select_product(row['apple_product_id'])
	if product_id == None:
		product_id = db.insert_row_dict('product', ['apple_product_id', 'product_sku', 'developer', 'product_name'], row)
	if date_id != None and product_id != None:
		row['date_id'] = date_id
		row['product_id'] = product_id
		db.insert_row_dict('daily_summary', ['date_id', 'product_id', 'product_version', 'transaction_type', 'units', 'customer_country', 'customer_currency', 'payment_currency', 'customer_price', 'payment_price'], row)


def import_from_filesystem(database_path, *file_list):
	db = its_database.SalesDatabase(database_path)
	db.open()
	reader = DailySummaryFileReader()
	
	for file_path in file_list:
		if os.path.isfile(file_path):
			files = [file_path]
		else:
			files = glob.glob(os.path.join(file_path, '*.txt.gz'))
		for file in files:
			success = reader.read_lambda(file, lambda row: import_into_database(db, row))
	
	db.close()


if __name__ == '__main__':
	show_usage = True
	if len(sys.argv) >= 3:
		database_path = sys.argv[1]
		file_path = sys.argv[2]
		show_usage = False
		import_from_filesystem(database_path, file_path)
	if show_usage:
		print 'Usage: its_import.py <database> <archive file or folder>'

