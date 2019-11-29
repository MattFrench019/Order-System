import flask

app = flask.Flask(__name__)


### --------Backend Handles------- ###
@app.route('/orders/get/all', methods=['GET'])
def get_orders():
	flask.abort(501, '501 Not Implemented')


@app.route('/orders/new', methods=['POST'])
def add_order():
	flask.abort(501, '501 Not Implemented')


@app.route('/orders/get/<int:order_id>', methods=['GET'])
def get_order(order_id):
	flask.abort(501, '501 Not Implemented')


@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
	flask.abort(501, '501 Not Implemented')



### -------Frontend Portals------- ###
@app.route('/waiter', methods=['GET'])
def waiter_portal():
	return flask.render_template('waiter.html')


@app.route('/chef', methods=['GET'])
def chef_portal():
	return flask.render_template('chef.html')


@app.route('/manager', methods=['GET'])
def manager_portal():
	return flask.render_template('manager.html')


if __name__ == '__main__':
	app.run(debug=True)
