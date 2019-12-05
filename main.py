from flask import request, jsonify, render_template, Flask

# Create flask app
app = Flask(__name__)


# Holds a list of orders
class OrderList:
	def __init__(self, _list):
		self._list = _list

	def get(self, _id):
		for order in self._list:
			if order.id == _id:
				return order
		return None

	def add(self, order):
		self._list.append(order)

	@property
	def list(self):
		return self._list

	@property
	def next_index(self):
		return self._list.__len__()

	@property
	def json(self):
		return_list = []
		for order in self._list:
			return_list.append(order.tuple)

		return return_list


# Holds several details for an order
class Order:
	def __init__(self, _id, _list, table):
		self.id = _id
		self.list = _list
		self.table = table

	@property
	def price(self):
		price = 0.0
		for item in self.list:
			price += items.get(item).price

		return round(price, 2)

	@property
	def tuple(self):
		return self.id, self.table, self.tuple_list, self.readable

	@property
	def readable(self):
		return f'({self.id}) - Table {self.table} £{self.price}'

	@property
	def tuple_list(self):
		return_list = []
		for item in self.list:
			return_list.append((item, items.get(item).name))

		return return_list


# Holds several details for an item
class Item:
	def __init__(self, name, price, _id):
		self.name = name
		self.price = price
		self.id = _id


# Holds a list of items
class ItemList:
	def __init__(self, _list):
		# Holds the list of items
		self._list = _list

	def get(self, _id):
		# Finds an item from an id
		for item in self._list:
			if item.id == _id:
				return item
		return None

	@property
	def list(self):
		return self._list


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

	orders.get(order_id).list = order_items

	print(orders.json)

	return jsonify(200)


### -------Frontend Portals------- ###
@app.route('/waiter', methods=['GET'])
def waiter_portal():
	return render_template('waiter.html', items=items.list, tables=tables)


@app.route('/chef', methods=['GET'])
def chef_portal():
	return render_template('chef.html')


@app.route('/manager', methods=['GET'])
def manager_portal():
	return render_template('manager.html')


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0")
