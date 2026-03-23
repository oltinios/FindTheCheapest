from flask import Flask, jsonify
import asyncio
from FindTheCheapest import main 

app = Flask(__name__)

@app.route("/items")
def get_items():
    data = asyncio.run(main())
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)