from flask import Flask, jsonify

app = Flask(__name__)
@app.route('/')
def home():
    return "Welcome to the Flask API!"


@app.route('/recommendations/<int:product_id>', methods=['GET'])
def get_recommendations(product_id):
    # For simplicity, return a static list of recommendations
    recommendations = [
        {"id": 1, "title": "Recommended Product 1"},
        {"id": 2, "title": "Recommended Product 2"},
    ]
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
