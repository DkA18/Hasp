# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# Basic route
@app.route('/')
def home():
    return jsonify({"message": "Hello, Home Assistant!"})

# Additional route example
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "service": "My Home Assistant Add-on"})

# Example route to handle POST requests
@app.route('/data', methods=['POST'])
def data():
    data = request.get_json()
    return jsonify({"received_data": data}), 201

if __name__ == '__main__':
    # Run the Flask app on all available network interfaces
    app.run(host='0.0.0.0', port=5000)
