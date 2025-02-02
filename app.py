from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route('/recommendations/<int:product_id>')
def recommend(product_id):
    # Your recommendation logic here
    return jsonify({"recommendations": [f"Product {product_id} - A", f"Product {product_id} - B", f"Product {product_id} - C"]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
