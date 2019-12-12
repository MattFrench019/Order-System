
class ListLogic:
	# Constructor
	def __init__(self, db_table, db):
		self.db_table = db_table
		self.db = db

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
		cursor = self.db.cursor()
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
	def __init__(self, db):
		super(OrderList, self).__init__('orders', db)

	def _create_objects(self, _list):
		new_list = []
		for order in _list:
			new_list.append(Order(order[0], order[1].split(','), order[2]))

		return new_list

	def edit(self, _id, _items):
		cursor = self.db.cursor()
		query = "UPDATE orders SET items = '{}' WHERE id = {};".format(str(_items)[1:-1], _id)
		cursor.execute(query)
		self.db.commit()

	def add(self, _object):
		cursor = self.db.cursor()
		query = "INSERT INTO orders (id, items, tablenum) VALUES ({}, '{}', {});".format(str(_object.id), str(_object.list)[1:-1], str(_object.table))
		cursor.execute(query)
		self.db.commit()

	# Returns a jsonify-ible version of the object
	@property
	def json(self):
		return_list = []
		for order in self.list:
			return_list.append(order.tuple)

		return return_list

	def delete(self, order_id):
		cursor = self.db.cursor()
		query = "DELETE FROM orders WHERE id = {};".format(order_id)
		cursor.execute(query)
		self.db.commit()


# Holds the details for an order
class Order:

	# Constructor
	def __init__(self, _id, _list, table, items_list):
		self.id = _id  # Id
		self.list = _list  # List of items
		self.table = table  # Table number
		self._items_list = items_list

	# Generates the price
	@property
	def price(self):
		price = 0.0

		items_list = self._items_list.list
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

		items_list = self._items_list.list
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
	def __init__(self, db):
		super(ItemList, self).__init__('items', db)

	def _create_objects(self, _list):
		new_list = []
		for item in _list:
			new_list.append(Item(item[1], item[2], item[0]))

		return new_list
