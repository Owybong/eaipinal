from flask import Flask, request, jsonify
from ariadne import graphql_sync, make_executable_schema, load_schema_from_path
from ariadne.explorer import ExplorerGraphiQL
from resolvers import query
import os

app = Flask(__name__)

# Get the current directory and load schema from it
current_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(current_dir, "schema.graphql")
type_defs = load_schema_from_path(schema_path)
schema = make_executable_schema(type_defs, query)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return ExplorerGraphiQL().html(None), 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    return jsonify(result)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Customer Service API. Please use the GraphQL endpoint at /graphql"})

if __name__ == "__main__":
    app.run(port=5002, debug=True)