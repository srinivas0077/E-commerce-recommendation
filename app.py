from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
import os
import uuid  # For generating random unique IDs

# Set the path to your custom templates and static folders
TEMPLATE_FOLDER = r"C:\Users\srini\OneDrive\Documents\real_time_recommendation_system\frontend"
STATIC_FOLDER = r"C:\Users\srini\OneDrive\Documents\real_time_recommendation_system\frontend\static"

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# Path to the CSV and XLSX files
CSV_FILE = r"C:\Users\srini\OneDrive\Documents\real_time_recommendation_system\ECommerce_consumer behaviour.csv"
XLSX_FILE = r"C:\Users\srini\OneDrive\Documents\real_time_recommendation_system\backend\recommendation_data.xlsx"

# Load data from the CSV file
def load_data():
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE)
        except Exception as e:
            raise Exception(f"Error loading CSV file: {e}")
    else:
        raise FileNotFoundError(f"CSV file not found at {CSV_FILE}")

# Load or initialize browsing data
def load_browsing_data():
    if os.path.exists(XLSX_FILE):
        try:
            browsing_data = pd.read_excel(XLSX_FILE)
            # Ensure user_id is treated as integer and clean any non-numeric values
            browsing_data["user_id"] = pd.to_numeric(browsing_data["user_id"], errors='coerce').fillna(0).astype(int)
            return browsing_data
        except Exception as e:
            raise Exception(f"Error loading XLSX file: {e}")
    else:
        return pd.DataFrame(columns=["timestamp", "user_id", "product_name", "category", "price"])

# Save browsing data
def save_browsing_data(data):
    try:
        data.to_excel(XLSX_FILE, index=False)
    except Exception as e:
        print(f"Error saving XLSX file: {e}")

# Load the data
try:
    data = load_data()
    browsing_data = load_browsing_data()
except Exception as e:
    print(f"Error: {e}")
    data = None
    browsing_data = pd.DataFrame(columns=["timestamp", "user_id", "product_name", "category", "price"])

# Function to log browsing activity with category, price, and timestamp
def log_browsing_activity(user_id, product_name, category, price):
    global browsing_data
    user_id = int(user_id)  # Ensure user_id is an integer

    # No need for product_id, as we are only focusing on product_name
    new_entry = pd.DataFrame(
        {
            "timestamp": [datetime.now()],
            "user_id": [user_id],
            "product_name": [product_name],
            "category": [category],
            "price": [price],
        }
    )
    browsing_data = pd.concat([browsing_data, new_entry], ignore_index=True)
    save_browsing_data(browsing_data)


# Function to generate recommendations based on search history
def recommend_based_on_search(user_id):
    try:
        if browsing_data.empty:
            return ["No search history available for recommendations."]

        user_searches = browsing_data[browsing_data["user_id"] == user_id]["product_name"]
        if user_searches.empty:
            return ["No search history available for this user."]

        # Combine search history with product catalog for similarity analysis
        all_products = pd.DataFrame(data["product_name"].unique(), columns=["product_name"])
        user_searches_df = pd.DataFrame(user_searches.unique(), columns=["product_name"])
        combined_data = pd.concat([user_searches_df, all_products], ignore_index=True).drop_duplicates()

        # Use TF-IDF to calculate product similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(combined_data["product_name"])
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Get indices of user searches in the combined data
        user_indices = [combined_data.index[combined_data["product_name"] == search].tolist()[0] for search in user_searches]

        # Aggregate similarity scores for all user searches
        similarity_scores = similarity_matrix[user_indices].sum(axis=0)

        # Sort by similarity and exclude already searched products
        combined_data["similarity"] = similarity_scores
        recommendations = combined_data[~combined_data["product_name"].isin(user_searches)].sort_values(
            by="similarity", ascending=False
        )

        top_recommendations = recommendations.head(5)["product_name"].tolist()
        return top_recommendations if top_recommendations else ["No recommendations found."]

    except Exception as e:
        print(f"Error in search-based recommendation logic: {e}")
        return ["An error occurred while generating recommendations."]


# Function to generate purchase-based recommendations (placeholder logic)
def recommend_based_on_purchase(user_id):
    try:
        # Placeholder logic: Recommend top 5 products purchased by other users
        if data.empty:
            return ["No purchase data available for recommendations."]

        # Get the most popular products from the data (assuming 'product_name' is the column to check)
        popular_products = data["product_name"].value_counts().head(5).index.tolist()
        return popular_products if popular_products else ["No recommendations found."]
    except Exception as e:
        print(f"Error in purchase-based recommendation logic: {e}")
        return ["An error occurred while generating recommendations."]



# Function to generate browsing-based recommendations (based on browsing activity)
def recommend_based_on_browsing(user_id):
    try:
        # Ensure user_id is treated as integer
        user_id = int(user_id)

        # Filter browsing data for the given user_id
        user_browsing = browsing_data[browsing_data["user_id"] == user_id]
        if user_browsing.empty:
            return ["No browsing history available for recommendations."]

        # Get unique product names based on browsing history
        recommended_products = user_browsing["product_name"].unique().tolist()
        return recommended_products if recommended_products else ["No recommendations found."]
    except Exception as e:
        print(f"Error in browsing-based recommendation logic: {e}")
        return ["An error occurred while generating recommendations."]

# Function to handle the browse route
@app.route('/browse', methods=['POST'])
def browse():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_name = data.get('product_name')
        category = data.get('category')
        price = data.get('price')

        if not user_id or not product_name or not category or not price:
            return jsonify({"error": "Missing required fields"}), 400

        # Log the browsing activity
        log_browsing_activity(user_id, product_name, category, price)

        # Process the search and return results (this should be replaced with actual logic)
        search_results = search_products(user_id, product_name, category, price)

        return jsonify({
            "message": f"Search results for {product_name} in category {category} at price {price}",
            "results": search_results
        })
    except Exception as e:
        print(f"Error in browse route: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Function to handle search-based product recommendation
def search_products(user_id, product_name, category, price):
    return [
        {"name": "Soap A", "category": "sl", "price": 200},
        {"name": "Soap B", "category": "sl", "price": 150}
    ]

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        user_id = request.json.get("user_id")
        based_on = request.json.get("based_on", "purchase")  # Default to 'purchase' if not provided
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid User ID. It must be a number."}), 400

        if based_on == "search":
            recommendations = recommend_based_on_search(user_id)
        elif based_on == "purchase":
            recommendations = recommend_based_on_purchase(user_id)
        elif based_on == "browse":
            recommendations = recommend_based_on_browsing(user_id)  # Handle browsing-based recommendations
        else:
            recommendations = ["Invalid recommendation type specified."]

        return jsonify({"recommendations": recommendations}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
