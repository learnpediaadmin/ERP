# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

test_ignore = ["Account", "Cost Center"]

import frappe
import unittest
from frappe.utils import random_string
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country

test_records = frappe.get_test_records('Company')

class TestCompany(unittest.TestCase):
	def test_coa_based_on_existing_company(self):
		company = frappe.new_doc("Company")
		company.company_name = "COA from Existing Company"
		company.abbr = "CFEC"
		company.default_currency = "INR"
		company.create_chart_of_accounts_based_on = "Existing Company"
		company.existing_company = "_Test Company"
		company.save()
		
		expected_results = {
			"Debtors - CFEC": {
				"account_type": "Receivable",
				"is_group": 0,
				"root_type": "Asset",
				"parent_account": "Accounts Receivable - CFEC",
			},
			"_Test Cash - CFEC": {
				"account_type": "Cash",
				"is_group": 0,
				"root_type": "Asset",
				"parent_account": "Cash In Hand - CFEC"
			}
		}
		
		for account, acc_property in expected_results.items():
			acc = frappe.get_doc("Account", account)
			for prop, val in acc_property.items():
				self.assertEqual(acc.get(prop), val)
				
		frappe.delete_doc("Company", "COA from Existing Company")
				
	def test_coa_based_on_country_template(self):
		countries = ["India", "Brazil", "United Arab Emirates", "Canada", "Germany", "France",
			"Guatemala", "Indonesia", "Mexico", "Nicaragua", "Netherlands", "Singapore"]
		
		for country in countries:
			templates = get_charts_for_country(country)
			if len(templates) != 1 and "Standard" in templates:
				templates.remove("Standard")
			
			self.assertTrue(templates)
			
			for template in templates:
				try:
					company = frappe.new_doc("Company")
					company.company_name = template
					company.abbr = random_string(3)
					company.default_currency = "USD"
					company.create_chart_of_accounts_based_on = "Standard Template"
					company.chart_of_accounts = template
					company.save()
				
					account_types = ["Cost of Goods Sold", "Depreciation", 
						"Expenses Included In Valuation", "Fixed Asset", "Payable", "Receivable", 
						"Stock Adjustment", "Stock Received But Not Billed", "Bank", "Cash", "Stock"]
				
					for account_type in account_types:
						filters = {
							"company": template,
							"account_type": account_type
						}
						if account_type in ["Bank", "Cash", "Stock"]:
							filters["is_group"] = 1

						self.assertTrue(frappe.get_all("Account", filters))
				finally:
					frappe.delete_doc("Company", template)