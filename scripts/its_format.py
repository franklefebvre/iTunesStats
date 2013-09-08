#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SalesFormatter:
	def __init__(self):
		self.minimum_sales_by_country = .1
	
	def format_product_sales_by_country(self, raw_list):
		# row[0] = country, row[1] = count
		total = 0
		for row in raw_list:
			total += row[1]
		filtered_list = []
		handled = 0
		for row in raw_list:
			if 1.0 * row[1] / total < self.minimum_sales_by_country:
				last_row = ['other', total - handled]
				filtered_list += [last_row]
				break
			else:
				filtered_list += [row]
				handled += row[1]
		return filtered_list
	
	def format_product_sales_by_version(self, raw_list):
		# row[0] = version, row[1] = transaction_type, row[2] = count
		result_dict = {}
		previous_version = None
		for row in raw_list:
			version = row[0]
			update = (row[1] in ['7', '7F', '7T', 'F7'])
			count = row[2]
			if update:
				if result_dict.has_key(previous_version):
					result_dict[previous_version] -= count
				result_dict[version] = count
			else:
				if result_dict.has_key(version):
					result_dict[version] += count
				else:
					result_dict[version] = count
			previous_version = version
		return [[k, v] for k, v in result_dict.iteritems()]
		# FIXME: sort
		# row[0] = version, row[1] = count
