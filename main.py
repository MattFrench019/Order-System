import flask

app = flask.Flask(__name__)


@app.route('/waiter', methods=['GET'])
def waiter_portal():
	flask.abort(501, '501 Not Implemented')


@app.route('/chef', methods=['GET'])
def chef_portal():
	flask.abort(501, '501 Not Implemented')


@app.route('/manager', methods=['GET'])
def manager_portal():
	flask.abort(501, '501 Not Implemented')


if __name__ == '__main__':
	app.run(debug=True)
