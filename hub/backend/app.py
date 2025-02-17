from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/api/data", methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        sensor_type = data.get("sensor")
        sensor_value = data.get("value")

        print(f"Received Data -> Sensor: {sensor_type}, Value: {sensor_value}")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "thanks!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
