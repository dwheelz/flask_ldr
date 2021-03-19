from flask import Flask, jsonify, request
from flask_expects_json import expects_json

from common.ldr_edge import TimeTillEdge


app = Flask(__name__, static_url_path="") # flask object

schema = {
    "properties": {
        "iterations": {"type": "integer"},
        "io_order": {"type": "integer"},
        "average_results": {"type": "boolean"},
        "stop_on_timeout": {"type": "boolean"}
    }
}

@app.route("/time_post", methods=["POST"])
@expects_json(schema)
def time_post() -> dict:
    """[summary]

    Args:
        gpio_object ([type]): [description]
    """
    pass


@app.route("/time_get", methods=["GET"])
def time_get() -> dict:
    """[summary]

    Returns:
        dict: [description]
    """
    with TimeTillEdge() as ldr:  # Using defaults
        return jsonify(ldr.poll_edge_time())


@app.route("/")
def test_flask() -> str:
    """
    simply for test
    :return: str
    """
    return "<h1>TEST PAGE FOR PI LDR</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=False)