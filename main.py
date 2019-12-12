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

import classes

configparser = RawConfigParser()
configparser.read('main.config')
config = configparser.get

ADMIN_PASSWORD = config('main-config', 'admin-password')
TIME_OUT = int(config('main-config', 'admin-timeout'))

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

# Init Items list
items = classes.ItemList(db)

# Init Orders list
orders = classes.OrderList(db, items)

# Init Tables
tables = range(1, int(config('main-config', 'tables')) + 1)


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
	orders.add(classes.Order(orders.next_index, order_items, table_num, items))

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
