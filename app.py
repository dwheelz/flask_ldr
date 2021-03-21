from pathlib import Path

from collections import namedtuple

from flask import Flask, jsonify, request
from flask_expects_json import expects_json

from json import load

from common.ldr_edge import TimeTillEdge


def get_conf(json_file="conf"):
    """Returns the GPIO configuration (pins used, mode, etc) from the config file

    Args:
        json_file (str, optional): Name of the config file (without file type). Defaults to "conf".

    Returns:
        object: A python object
    """
    full_path = Path(__file__).parent.absolute()
    with open(Path(full_path, "config", json_file + ".json"), "r") as conf:
        return load(conf, object_hook=lambda d: namedtuple('config', d.keys())(*d.values()))


# --- DEFINE POST SCHEMA ---
schema = {
    "properties": {
        "iterations": {"type": "integer"},
        "io_order": {"type": "integer"},
        "average_results": {"type": "boolean"},
        "stop_on_timeout": {"type": "boolean"}
    }
}

# --- INIT FLASK OBJECT AND CONFIG VALUES ---
app = Flask(__name__, static_url_path="") # flask object
ldr_config = get_conf()

@app.route("/ldr_time", methods=["GET", "POST"])
@expects_json(schema, ignore_for=['GET'])
def ldr_time() -> str:
    """The time it took to hit a rising or falling edge

    Returns:
        json string: The response from the LDR edge time query, example below:
            {
                "0":{"time":2.75,"timeout":false},
                "1":{"time":2.88,"timeout":false},
                "2":{"time":2.83,"timeout":false},
                "average":2.82
            }

    """
    with TimeTillEdge(*ldr_config) as ldr:  # Using defaults
        if request.method == "POST":
            post_data = request.get_json()
            try:

                return_vals = ldr.poll_edge_time(**post_data)

            except TypeError as te:
                return jsonify({"error": str(te)})

        else:
            return_vals = ldr.poll_edge_time()

        return jsonify(return_vals)


@app.route("/")
def test_flask() -> str:
    """
    simply for test
    :return: str
    """
    return "<h1>TEST PAGE FOR PI LDR</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=False)