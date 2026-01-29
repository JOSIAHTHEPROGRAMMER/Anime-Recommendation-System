from flask import Flask, request, jsonify
from flask_cors import CORS
from animeml import recommend, metadata
import sys

app = Flask(__name__)
CORS(app)

# Suppress Flask development warning with a custom message
print("=" * 60)
print("Anime Recommendation API")
print("=" * 60)

@app.route("/")
def home():
    """API documentation endpoint"""
    return jsonify({
        "message": "Anime Recommendation API",
        "endpoints": {
            "/titles": "GET - List all available anime titles",
            "/recommend": "GET - Get recommendations (param: title, top_n)",
            "/search": "GET - Search titles (param: query)",
            "/info": "GET - Get anime info (param: title)"
        },
        "examples": {
            "titles": "/titles",
            "recommend": "/recommend?title=Naruto&top_n=5",
            "search": "/search?query=one piece",
            "info": "/info?title=Naruto"
        },
        "total_anime": len(metadata)
    })


@app.route("/titles")
def titles():
    """Get all available anime titles"""
    print("Request: Get all titles")
    title_list = sorted(metadata['title'].dropna().unique().tolist())
    return jsonify({
        "count": len(title_list),
        "titles": title_list
    })


@app.route("/recommend")
def get_recommendations():
    """Get anime recommendations"""
    title = request.args.get("title")
    top_n = request.args.get("top_n", 5, type=int)
    
    if not title:
        return jsonify({
            "error": "Missing 'title' parameter",
            "example": "/recommend?title=Naruto&top_n=5"
        }), 400
    
    # Validate top_n
    top_n = min(max(1, top_n), 50)  # Between 1 and 50
    
    print(f"Request: Recommendations for '{title}' (top {top_n})")
    
    try:
        results = recommend(title, top_n=top_n)
        
        if not results:
            # Try to find similar titles
            similar = []
            title_lower = title.lower()
            for t in metadata['title'].dropna().values:
                if title_lower in str(t).lower():
                    similar.append(str(t))
                    if len(similar) >= 5:
                        break
            
            return jsonify({
                "error": f"Anime '{title}' not found",
                "suggestions": similar
            }), 404
        
        print(f"Returning {len(results)} recommendations")
        
        return jsonify({
            "query": title,
            "count": len(results),
            "recommendations": results
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route("/search")
def search():
    """Search for anime titles"""
    query = request.args.get("query", "").lower()
    limit = request.args.get("limit", 20, type=int)
    
    if not query:
        return jsonify({
            "error": "Missing 'query' parameter",
            "example": "/search?query=naruto&limit=20"
        }), 400
    
    limit = min(max(1, limit), 100)
    
    print(f"Request: Search for '{query}'")
    
    # Search in titles
    matches = []
    for title in metadata['title'].dropna().values:
        if query in str(title).lower():
            matches.append(str(title))
            if len(matches) >= limit:
                break
    
    print(f"Found {len(matches)} matches")
    
    return jsonify({
        "query": query,
        "count": len(matches),
        "results": matches
    })


@app.route("/info")
def info():
    """Get detailed information about a specific anime"""
    title = request.args.get("title")
    
    if not title:
        return jsonify({
            "error": "Missing 'title' parameter",
            "example": "/info?title=Naruto"
        }), 400
    
    print(f"Request: Info for '{title}'")
    
    # Find the anime in metadata
    anime_info = metadata[metadata['title'] == title]
    
    if anime_info.empty:
        # Try case-insensitive search
        anime_info = metadata[metadata['title'].str.lower() == title.lower()]
    
    if anime_info.empty:
        return jsonify({
            "error": f"Anime '{title}' not found"
        }), 404
    
    # Convert to dict (first match)
    info_dict = anime_info.iloc[0].to_dict()
    
    # Remove NaN values
    info_dict = {k: v for k, v in info_dict.items() if v == v}  # NaN != NaN
    
    return jsonify(info_dict)


@app.route("/random")
def random_anime():
    """Get random anime"""
    count = request.args.get("count", 1, type=int)
    count = min(max(1, count), 20)
    
    print(f"Request: {count} random anime")
    
    random_titles = metadata['title'].dropna().sample(n=count).tolist()
    
    return jsonify({
        "count": len(random_titles),
        "titles": random_titles
    })


@app.route("/stats")
def stats():
    """Get dataset statistics"""
    stats_dict = {
        "total_anime": len(metadata),
        "columns": list(metadata.columns),
        "sample_titles": metadata['title'].dropna().head(5).tolist()
    }
    
    # Add type distribution if available
    if 'type' in metadata.columns:
        stats_dict['types'] = metadata['type'].value_counts().to_dict()
    
    # Add genre stats if available
    if 'genre' in metadata.columns:
        stats_dict['total_genres'] = metadata['genre'].nunique()
    
    return jsonify(stats_dict)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/titles", "/recommend", "/search", "/info", "/random", "/stats"]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


if __name__ == "__main__":
    print("\nStarting server...")
    print("\nAvailable endpoints:")
    print("  • http://localhost:5000/")
    print("  • http://localhost:5000/titles")
    print("  • http://localhost:5000/recommend?title=Naruto")
    print("  • http://localhost:5000/search?query=naruto")
    print("  • http://localhost:5000/info?title=Naruto")
    print("  • http://localhost:5000/random")
    print("  • http://localhost:5000/stats")
    print("\n" + "=" * 60)
    
    # Get port from environment or use default
    import os
    port = int(os.getenv("PORT", 5000))
    
    # For development - use Flask's built-in server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )