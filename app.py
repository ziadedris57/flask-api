from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import secrets
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Configure Flask to use the database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Example: "active" or "inactive"

    def __repr__(self):
        return f"<User {self.email}>"

# Create the database tables
with app.app_context():
    db.create_all()



api_keys = {}
@app.route('/generate-api-key', methods=['POST'])
def generate_api_key():
    # Generate a new API key
    api_key = secrets.token_hex(16)  # Generate a random hex token

    # Store the API key (In a real application, store it in a database)
    api_keys[api_key] = {"active": True}  # You can add more metadata if needed

    return jsonify({"api_key": api_key}), 201

@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json

    # Extract inputs
    products = data.get("products", [])
    target_product_id = data.get("target_product_id")
    selected_attributes = data.get("attributes", [])
    weights = data.get("weights", {})

    if not products or target_product_id is None:
        return jsonify({"error": "Products list and target_product_id are required"}), 400

    # Find target product by ID
    target_product = next((p for p in products if p["id"] == target_product_id), None)
    if not target_product:
        return jsonify({"error": "Target product ID not found in products"}), 400

    # If attributes are not provided, use all attributes except ID
    if not selected_attributes:
        selected_attributes = [key for key in products[0].keys() if key != "id"]

    # If weights are not provided, assign equal weights
    if not weights:
        weights = {attr: 1.0 / len(selected_attributes) for attr in selected_attributes}

    # Create text representations for each product based on selected attributes
    product_texts = []
    for product in products:
        weighted_text = " ".join(
            (str(product.get(attr, "")) + " ") * int(weights.get(attr, 1) * 10)
            for attr in selected_attributes
        )
        product_texts.append(weighted_text.strip())

    # Compute similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(product_texts)
    similarity_scores = cosine_similarity(tfidf_matrix)

    # Get target product index
    target_index = next(i for i, p in enumerate(products) if p["id"] == target_product_id)

    # Rank products based on similarity
    scores = list(enumerate(similarity_scores[target_index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # Get top 5 recommendations (excluding the target product itself)
    recommended_products = [products[i]["id"] for i, score in scores if i != target_index][:5]

    return jsonify({"recommended_product_ids": recommended_products})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
