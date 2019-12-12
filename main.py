"""
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

# Compatibility
from __future__ import print_function

# Used for cookie authenticatiom
from time import time

# Imports optimised for readability
from flask import request, jsonify, render_template, Flask, make_response

# For connection to DB
import mysql.connector as sql

# For parsing config file
from configparser import RawConfigParser

configparser = RawConfigParser()
configparser.read('main.config')
config = configparser.get

ADMIN_PASSWORD = config('main-config', 'admin-password')
TIME_OUT = config('main-config', 'admin-timeout')

# Create flask app
app = Flask(__name__)



unix_sock = '/cloudsql/{}'.format(config('main-config', 'db-connection-name'))

# Connection to DB
db = sql.connect(
	unix_socket=unix_sock,
	user=config('main-config', 'db-user'),
	password=config('main-config', 'db-password'),
	database=config('main-config', 'db-name')
)


class ListLogic:
	# Constructor
	def __init__(self, db_table):
		self.db_table = db_table

	# Logic to add a new object to the table
	def add(self, _object):
		pass

	# Logic to find Order object by the Id of the order
	def get(self, _id):
		pass

	def _create_objects(self, _list):
		pass

	# Public getter for private list
	@property
	def list(self):
		cursor = db.cursor()
		cursor.execute('SELECT * FROM {}'.format(self.db_table))

		return sorted(self._create_objects(cursor.fetchall()), key=lambda x: x.id)

	# Public getter for the next id for a new order
	@property
	def next_index(self):
		biggest_index = 0
		for order in self.list:
			if order.id > biggest_index:
				biggest_index = order.id

		return biggest_index + 1


# Holds a list of Order objects
class OrderList(ListLogic):

	# Constructor
	def __init__(self):
		super(OrderList, self).__init__('orders')

	def _create_objects(self, _list):
		new_list = []
		for order in _list:
			new_list.append(Order(order[0], order[1].split(','), order[2]))

		return new_list

	def edit(self, _id, _items):
		cursor = db.cursor()
		query = "UPDATE orders SET items = '{}' WHERE id = {};".format(str(_items)[1:-1], _id)
		cursor.execute(query)
		db.commit()

	def add(self, _object):
		cursor = db.cursor()
		query = "INSERT INTO orders (id, items, tablenum) VALUES ({}, '{}', {});".format(str(_object.id), str(_object.list)[1:-1], str(_object.table))
		cursor.execute(query)
		db.commit()

	# Returns a jsonify-ible version of the object
	@property
	def json(self):
		return_list = []
		for order in self.list:
			return_list.append(order.tuple)

		return return_list

	def delete(self, order_id):
		cursor = db.cursor()
		query = "DELETE FROM orders WHERE id = {};".format(order_id)
		cursor.execute(query)
		db.commit()


# Holds the details for an order
class Order:

	# Constructor
	def __init__(self, _id, _list, table):
		self.id = _id  # Id
		self.list = _list  # List of items
		self.table = table  # Table number

	# Generates the price
	@property
	def price(self):
		price = 0.0

		items_list = items.list
		items_list = [x.price for x in items_list]

		for item in self.list:
			price += items_list[int(item) - 1]

		# Round to avoid floating-point rounding errors
		return round(price, 2)

	# Returns a tuple with all important attributes
	@property
	def tuple(self):
		return self.id, self.table, self.tuple_list, self.readable

	# Used to show the order on the front-end
	@property
	def readable(self):
		return str(self.id) + ' - Table ' + str(self.table) + ' £' + str(self.price)

	# Returns an array of items with the item id and the item name
	# Used in the edit menu
	@property
	def tuple_list(self):
		return_list = []

		items_list = items.list
		items_list = [x.name for x in items_list]

		for item in self.list:
			return_list.append((item, items_list[int(item) - 1]))

		return return_list


# Holds several details for an item
class Item:
	# Constructor
	def __init__(self, name, price, _id):
		self.name = name
		self.price = price
		self.id = _id


# Holds a list of items
class ItemList(ListLogic):
	# Constructor
	def __init__(self):
		super(ItemList, self).__init__('items')

	def _create_objects(self, _list):
		new_list = []
		for item in _list:
			new_list.append(Item(item[1], item[2], item[0]))

		return new_list


# Init Items list
items = ItemList()

# Init Orders list
orders = OrderList()

# Init Tables
tables = range(1, config('main-config', 'tables') + 1)


### --------Backend Handles------- ###

# Handles when the front-end wants to get a list of orders
@app.route('/orders/get/all', methods=['GET'])
def get_orders():
	# Returns a JSON list of all items in the OrderList
	return jsonify(orders.json)


# Handles when the front-end wants to create a new order
@app.route('/orders/new', methods=['GET', 'POST'])
def add_order():
	# Gets the list of order items by splitting the url argument into individual components
	order_items = request.args.get('items').split(',')

	# We need to turn all of the values into integers
	order_items = [int(x) for x in order_items]

	# Get the table number from the url query
	table_num = request.args.get('table')

	# Create the new order
	orders.add(Order(orders.next_index, order_items, table_num))

	# Return a :)
	return jsonify(200)


@app.route('/orders/edit', methods=['GET', 'POST'])
def edit_order():
	# Gets the list of order items by splitting the url argument into individual components
	order_items = request.args.get('items').split(',')

	# Order id
	order_id = int(request.args.get('id'))

	if order_items == ['']:
		orders.delete(order_id)
		return jsonify(200)

	# We need to turn all of the values into integers
	order_items = [int(x) for x in order_items]

	# Update the order's list of items
	orders.edit(order_id, order_items)

	# Return a :)
	return jsonify(200)


@app.route('/admin/backend', methods=['GET', 'POST'])
def admin_backend():
	full_cmd = request.args.get('cmd')
	cmd = full_cmd[0:6].upper()
	sub_cmd = full_cmd[7:]

	if request.cookies.get('admin_auth') is None:
		auth = False

	else:
		if time() <= float(request.cookies.get('admin_auth')):
			auth = True

		elif time() >= float(request.cookies.get('admin_auth')):
			auth = False

		else:
			auth = False


	if cmd == 'SIGNIN':
		if sub_cmd == ADMIN_PASSWORD:
			response = make_response('Login Accepted')
			response.set_cookie('admin_auth', str(int(time()) + TIME_OUT))
			return response
		else:
			return 'Invalid Login'

	elif cmd == 'HELPME':
		return 'Current commands are:\
				\n HELPME - Get help with commands\
				\n SIGNIN <password> - Authenticate with the server\
				\n RELOAD - Forces a reconnect to the database\n'

	elif cmd == 'RELOAD' and auth is True:
		db.reconnect()
		return 'Reconnected'

	elif auth is False:
		return 'Authentication Needed'

	else:
		return 'Command Error'


### -------Frontend Portal------- ###
@app.route('/waiter', methods=['GET'])
def waiter_portal():
	return render_template('waiter.html', items=items.list, tables=tables)


@app.route('/admin', methods=['GET'])
def admin_portal():
	response = make_response(render_template('admin.html'))
	return response


# Main
if __name__ == '__main__':
	# Host 0.0.0.0 exposes the app to other computers
	# Host 127.0.0.1 is only on the loop-back
	app.run(debug=True, host="0.0.0.0")
