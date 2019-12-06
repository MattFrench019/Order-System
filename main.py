# Compatibility
from __future__ import print_function

# Imports optimised for readability
from flask import request, jsonify, render_template, Flask

# Create flask app
app = Flask(__name__)


class ListLogic:
	# Constructor
	def __init__(self, _list):
		# Takes list and stores to private list
		self._list = _list

	# Logic to add a new order object to
	def add(self, order):
		self._list.append(order)

	# Logic to find Order object by the Id of the order
	def get(self, _id):

		# Loop through all items in private list
		for item in self._list:
			if item.id == _id:
				return item

		# Return None if not found
		return None

	# Public getter for private list
	@property
	def list(self):
		return self._list


# Holds a list of Order objects
class OrderList(ListLogic):

	# Constructor
	def __init__(self, _list):
		super(OrderList, self).__init__(_list)

	# Public getter for the next id for a new order
	@property
	def next_index(self):
		biggest_index = 0
		for order in self._list:
			if order.id > biggest_index:
				biggest_index = order.id

		return biggest_index

	# Returns a jsonify-ible version of the object
	@property
	def json(self):
		return_list = []
		for order in self._list:
			return_list.append(order.tuple)

		return return_list


# Holds the details for an order
class Order:

	# Constructor
	def __init__(self, _id, _list, table):
		self.id = _id       # Id
		self.list = _list   # List of items
		self.table = table  # Table number

	# Generates the price
	@property
	def price(self):
		price = 0.0
		for item in self.list:
			price += items.get(item).price

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
		for item in self.list:
			return_list.append((item, items.get(item).name))

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
	def __init__(self, _list):
		super(ItemList, self).__init__(_list)


# Init Items list
items = ItemList([
	Item('All Day Breakfast (L)', 5.5, 1),
	Item('All Day Breakfast (S)', 3.5, 2),
	Item('Hot Dog', 3.0, 3),
	Item('Burger', 4.0, 4),
	Item('Cheese Burger', 4.25, 5),
	Item('Chicken Goujons', 3.5, 6),
	Item('Fries', 1.75, 7),
	Item('Salad', 2.2, 8),
	Item('Milkshake', 1.3, 9),
	Item('Soft Drink', 1.3, 10),
	Item('Still Water', 0.9, 11),
	Item('Sparkling Water', 0.9, 12),
	Item('Coffee', 0.8, 13)
])

# Init Orders list
orders = OrderList([])

# Init Tables
tables = range(1, 12 + 1)


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

	# We need to turn all of the values into integers
	order_items = [int(x) for x in order_items]

	# Update the order's list of items
	orders.get(order_id).list = order_items

	# Return a :)
	return jsonify(200)


### -------Frontend Portal------- ###
@app.route('/waiter', methods=['GET'])
def waiter_portal():
	return render_template('waiter.html', items=items.list, tables=tables)


# Main
if __name__ == '__main__':
	# Host 0.0.0.0 exposes the app to other computers
	# Host 127.0.0.1 is only on the loop-back
	app.run(debug=True, host="0.0.0.0")
