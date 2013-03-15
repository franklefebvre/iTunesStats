#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys


class SalesDatabase:
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)
		self.conn.row_factory = sqlite3.Row
	
	def open(self):
		DATABASE_INITIALIZATION_STEPS = (
			'''
			CREATE TABLE IF NOT EXISTS report_date (
				date_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				date VARCHAR(10) NOT NULL,
				UNIQUE (date)
			)
			''',
			'''
			CREATE TABLE IF NOT EXISTS product (
				product_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				apple_product_id VARCHAR(18) NOT NULL,
				product_sku VARCHAR(100),
				iap_parent_sku VARCHAR(100),
				product_name VARCHAR(600),
				developer VARCHAR(4000),
				UNIQUE (apple_product_id)
			)
			''',
			'''
			CREATE TABLE IF NOT EXISTS daily_summary (
				transaction_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				date_id INTEGER NOT NULL,
				product_id INTEGER NOT NULL,
				product_version VARCHAR(100),
				transaction_type VARCHAR(20),
				units INTEGER,
				customer_country VARCHAR(2),
				customer_currency VARCHAR(3),
				payment_currency VARCHAR(3),
				customer_price DECIMAL(18,2) NOT NULL,
				payment_price DECIMAL(18,2) NOT NULL,
				promo_code VARCHAR(10),
				subscription_type VARCHAR(10),
				subscription_period VARCHAR(30),
				FOREIGN KEY (date_id) REFERENCES report_date(date_id),
				FOREIGN KEY (product_id) REFERENCES product(product_id),
				UNIQUE (date_id, product_id, product_version, transaction_type, customer_country)
			)
			''',
			"CREATE INDEX IF NOT EXISTS report_date_idx ON report_date (date)",
			"CREATE INDEX IF NOT EXISTS product_idx ON product (apple_product_id)",
			"CREATE INDEX IF NOT EXISTS ds_report_date_idx ON daily_summary (date_id)",
			"CREATE INDEX IF NOT EXISTS ds_product_idx ON daily_summary (product_id)",
			"CREATE INDEX IF NOT EXISTS ds_country_idx ON daily_summary (customer_country)",
			"CREATE INDEX IF NOT EXISTS ds_transaction_idx ON daily_summary (transaction_type)"
			)
		self.cursor = self.conn.cursor()
		for step in DATABASE_INITIALIZATION_STEPS:
			self.cursor.execute(step)
		self.conn.commit()
	
	def insert_row_dict(self, table, columns, data):
		query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(columns), ','.join(['?']*len(columns)))
		values = [data[key] for key in columns]
		try:
			self.cursor.execute(query, values)
			rowid = self.cursor.lastrowid
			self.conn.commit()
			return rowid
		except sqlite3.IntegrityError as e:
			print 'Integrity warning: {0}'.format(e)
			return None
	
	def select_product(self, apple_product_id):
		query = 'SELECT product_id FROM product WHERE apple_product_id = ?'
		self.cursor.execute(query, [apple_product_id])
		result = self.cursor.fetchone()
		if result:
			result = result[0]
		return result
	
	def select_date(self, report_date):
		query = 'SELECT date_id FROM report_date WHERE date = ?'
		self.cursor.execute(query, [report_date])
		result = self.cursor.fetchone()
		if result:
			result = result[0]
		return result
	
	def select_all_products(self):
		query = 'SELECT product_id, product_name, developer, apple_product_id, product_sku, iap_parent_sku FROM product ORDER BY product_name;'
		self.cursor.execute(query)
		result = self.cursor.fetchall()
		return result
	
	def select_product_sales_by_date(self, product_id):
		query = 'SELECT date, SUM(units) AS total FROM daily_summary, report_date WHERE daily_summary.date_id = report_date.date_id AND daily_summary.product_id = ? AND transaction_type in ("1", "1F", "1T", "F1") GROUP BY date ORDER BY date;'
		self.cursor.execute(query, [product_id])
		result = self.cursor.fetchall()
		return result
	
	def select_product_sales_by_country(self, product_id):
		query = 'SELECT customer_country, SUM(units) AS total FROM daily_summary WHERE product_id = ? AND transaction_type in ("1", "1F", "1T", "F1") GROUP BY customer_country ORDER BY total DESC;'
		self.cursor.execute(query, [product_id])
		result = self.cursor.fetchall()
		return result
	
	def select_product_sales_by_version(self, product_id):
		query = 'SELECT product_version, transaction_type, SUM(units) FROM daily_summary WHERE product_id = ? GROUP BY product_version, transaction_type ORDER BY product_version, transaction_type DESC;'
		self.cursor.execute(query, [product_id])
		result = self.cursor.fetchall()
		return result
	
	def close(self):
		self.cursor.close()
		self.cursor = None


	

if __name__ == '__main__':
	show_usage = True
	if len(sys.argv) >= 2:
		command = sys.argv[1]
		args = sys.argv[2:]
		if command == 'get' and len(args) == 5:
			(database, destination, login, password, vendorid) = args
			file = get_from_itunes_connect(login, password, vendorid, destination)
			if file:
				import_from_filesystem(database, file)
			show_usage = False
		if command == 'import' and len(args) >= 2:
			database = args[0]
			files = args[1:]
			import_from_filesystem(database, *files)
			show_usage = False
	if show_usage:
		print 'Usage: sqlite-import.py import <database> <path ...>'
	
#	import_from_filesystem('/Users/frank/Desktop/appstore-stats.db', '/Users/frank/Projects/Snippets/AppSales')

