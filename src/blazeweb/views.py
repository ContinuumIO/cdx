from app import app


@app.route("/data/<path:datapath>", methods=['GET'])
def get_data(datapath):
	return datapath

@app.route("/data/<path:datapath>", methods=['DELETE'])
def delete_data(path):
	pass

@app.route("/data/<path:datapath>", methods=['POST'])
def create_data(path):
	pass

@app.route("/data/<path:datapath>", methods=['PATCH'])
def update_data(path):
	pass

