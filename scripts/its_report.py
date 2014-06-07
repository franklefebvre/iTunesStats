#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import sys
import codecs
from datetime import datetime
from mako.template import Template
import ConfigParser

import its_database
import its_format


def days_from_epoch(date_str):
	d = datetime.strptime(date_str[:10], "%Y-%m-%d")
	return d.toordinal() - datetime(1970,1,1).toordinal()


class SalesReporter:
	def __init__(self, database, template_dir, output_dir):
		self.database = database
		self.template_dir = template_dir
		self.output_dir = output_dir
		self.formatter = its_format.SalesFormatter()
	
	def generate_product_sales_by_country_json(self, product_id):
		raw_rows = self.database.select_product_sales_by_country(product_id)
		# row[0] = country, row[1] = sales
		rows = self.formatter.format_product_sales_by_country(raw_rows)
		row_json_strings = ['{data: [[0, %s]], label: "%s"}' % (row[1], row[0]) for row in rows]
		array_json_string = '[' + ', '.join(row_json_strings) + ']'
		return array_json_string
		
	def generate_product_sales_by_date_json(self, product_id):
		rows = self.database.select_product_sales_by_date(product_id)
		# row[0] = date, row[1] = sales
		row_json_strings = ['[%d, %s]' % (days_from_epoch(rows[x][0]), rows[x][1]) for x in range(len(rows))]
		array_json_string= '[' + ', '.join(row_json_strings) + ']'
		return array_json_string
		
	def generate_product_sales_by_version_json(self, product_id):
		raw_rows = self.database.select_product_sales_by_version(product_id)
		# row[0] = version, row[1] = transaction_type, row[2] = count
		rows = self.formatter.format_product_sales_by_version(raw_rows)
		# row[0] = version, row[1] = count
		row_json_strings = ['{data: [[0, %s]], label: "%s"}' % (row[1], row[0]) for row in rows]
		array_json_string = '[' + ', '.join(row_json_strings) + ']'
		return array_json_string
	
	def generate_product_info_dict(self, product_id):
		info_dict = {}
		rows = self.database.select_product_sales_by_date(product_id)
		# row[0] = date, row[1] = sales
		if len(rows):
			info_dict['first_date'] = rows[0][0][:10]
			info_dict['latest_date'] = rows[-1][0][:10]
			info_dict['latest_day_sales'] = rows[-1][1]
			info_dict['total_sales'] = sum([v for [k,v] in rows])
		return info_dict
		
	def generate_root_files(self, products, product_info):
		files = glob.glob(os.path.join(self.template_dir, 'template-*'))
		for template_path in files:
			template_name = os.path.basename(template_path)
			pos = len('template-')
			output_name = template_name[pos:]
			output_path = os.path.join(self.output_dir, output_name)
			f = codecs.open(output_path, 'w', 'utf-8')
			template = Template(filename=template_path)
			f.write(template.render_unicode(products=products, product_info=product_info))
			f.close()
	
	def write_json_file(self, prefix, product_id, json_string):
		output_file_path = os.path.join(self.output_dir, '%s-%s.json' % (prefix, product_id))
		f = codecs.open(output_file_path, 'w', 'utf-8')
		f.write(json_string)
		f.close()
		
	def generate_all_files(self):
		products = self.database.select_all_products()
		product_info = {}
		for product in products:
			product_id = product[0]
			json_string = self.generate_product_sales_by_date_json(product_id)
			self.write_json_file('date', product_id, json_string)
			json_string = self.generate_product_sales_by_country_json(product_id)
			self.write_json_file('country', product_id, json_string)
			json_string = self.generate_product_sales_by_version_json(product_id)
			self.write_json_file('version', product_id, json_string)
			info_dict = self.generate_product_info_dict(product_id)
			product_info[product_id] = info_dict
		self.generate_root_files(products, product_info)


def generate_report(config_path):
	parser = ConfigParser.SafeConfigParser()
	parser.read(config_path)
	database_path = parser.get('data', 'database')
	template_dir = parser.get('report', 'templates')
	output_dir = parser.get('report', 'output')
	database = its_database.SalesDatabase(database_path)
	database.open()
	reporter = SalesReporter(database, template_dir, output_dir)
	reporter.generate_all_files()
	database.close()


if __name__ == '__main__':
	database = its_database.SalesDatabase('test.db')
	database.open()
	reporter = SalesReporter(database, 'templates', '.')
	reporter.generate_all_files()
	database.close()
