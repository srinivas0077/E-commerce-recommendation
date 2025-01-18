// Fetch recommendations based on browsing, purchase, or search history
function getRecommendations(basedOn) {
    let userId;

    if (basedOn === "browse") {
        userId = document.getElementById("browse_user_id").value;
    } else if (basedOn === "purchase") {
        userId = document.getElementById("recommend_user_id").value;
    }

    if (!userId) {
        alert("Please enter a User ID.");
        return;
    }

    fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, based_on: basedOn }), // Pass based_on correctly
    })
        .then((response) => response.json())
        .then((data) => {
            let recommendationsDiv;
            if (basedOn === "browse") {
                recommendationsDiv = document.getElementById("browsing_recommendations");
            } else if (basedOn === "purchase") {
                recommendationsDiv = document.getElementById("recommendations");
            }
            recommendationsDiv.innerHTML = "";

            if (data.error) {
                recommendationsDiv.innerHTML = `<p>${data.error}</p>`;
            } else if (data.recommendations && data.recommendations.length > 0) {
                const list = document.createElement("ul");
                data.recommendations.forEach((item) => {
                    const listItem = document.createElement("li");
                    listItem.textContent = item;
                    list.appendChild(listItem);
                });
                recommendationsDiv.appendChild(list);
            } else {
                recommendationsDiv.innerHTML = "<p>No recommendations available.</p>";
            }
        })
        .catch((error) => {
            console.error("Error fetching recommendations:", error);
        });
}

// Log browsing activity with category and price
function searchProducts() {
    const userId = document.getElementById("user_id").value;
    const query = document.getElementById("search_query").value;
    const category = document.getElementById("category").value;
    const price = document.getElementById("price").value;

    if (!userId || !query || !category || !price) {
        alert("Please enter User ID, search query, category, and price.");
        return;
    }

    fetch("/browse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, product_name: query, category: category, price: price }),
    })
        .then((response) => response.json())
        .then((data) => {
            const searchResults = document.getElementById("search_results");
            if (data.error) {
                searchResults.innerHTML = `<p>${data.error}</p>`;
            } else if (data.message) {
                searchResults.innerHTML = `<p>${data.message}</p>`;
            } else {
                searchResults.innerHTML = "<p>No results found.</p>";
            }
        })
        .catch((error) => {
            console.error("Error logging browsing activity:", error);
        });
}
