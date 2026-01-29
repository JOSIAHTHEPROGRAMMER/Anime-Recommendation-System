import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import time

# Configuration
CSV_PATH = "final_animedataset.csv"
SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 10000))

print("Loading anime dataset...")
start_time = time.time()

# Load data
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df):,} anime entries in {time.time() - start_time:.2f}s")

# Sample if dataset is too large
if len(df) > SAMPLE_SIZE:
    print(f"Sampling {SAMPLE_SIZE:,} entries for performance...")
    df = df.sample(n=SAMPLE_SIZE, random_state=42).reset_index(drop=True)


# Weight important features by repeating them in the tags
def create_tags(row):
    tags = []
    
    # Title is most important - include 3 times
    if pd.notna(row.get('title')):
        tags.extend([str(row['title'])] * 3)
    
    # Genres are very important - include 2 times
    if pd.notna(row.get('genre')):
        genres = str(row['genre']).replace(',', ' ').split()
        tags.extend(genres * 2)
    
    # Type and source
    if pd.notna(row.get('type')):
        tags.append(str(row['type']))
    
    if pd.notna(row.get('source')):
        tags.append(str(row['source']))
    
    # Add studio if available
    if 'studio' in row and pd.notna(row.get('studio')):
        studio = str(row['studio']).replace(',', ' ')
        tags.append(studio)
    
    # Categorize by score
    if 'score' in row and pd.notna(row.get('score')):
        try:
            score = float(row['score'])
            if score >= 8.0:
                tags.append('highly_rated')
            elif score >= 7.0:
                tags.append('well_rated')
            elif score >= 6.0:
                tags.append('decent_rated')
        except:
            pass
    
    # Categorize by episode count
    if 'episodes' in row and pd.notna(row.get('episodes')):
        try:
            eps = int(row['episodes'])
            if eps == 1:
                tags.append('movie_format')
            elif eps <= 13:
                tags.append('short_series')
            elif eps <= 26:
                tags.append('standard_series')
            else:
                tags.append('long_series')
        except:
            pass
    
    # Add era classification
    if 'aired' in row and pd.notna(row.get('aired')):
        try:
            import re
            year_str = str(row['aired'])
            years = re.findall(r'\b(19\d{2}|20\d{2})\b', year_str)
            if years:
                year = int(years[0])
                if year >= 2020:
                    tags.append('recent_anime')
                elif year >= 2010:
                    tags.append('modern_era')
                elif year >= 2000:
                    tags.append('early_2000s')
                else:
                    tags.append('classic_anime')
        except:
            pass
    
    return ' '.join(tags)

print("Creating enhanced tags...")
df['tags'] = df.apply(create_tags, axis=1)

# Store metadata with all available fields
metadata_cols = ['title', 'genre', 'type', 'source']
for col in ['score', 'episodes', 'aired', 'studio']:
    if col in df.columns:
        metadata_cols.append(col)

metadata = df[metadata_cols].reset_index(drop=True)

# Use TF-IDF to give better weight to important terms
print("Vectorizing content...")
cv = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2),  
    min_df=2,  #
    max_df=0.8 
)

vectorized = cv.fit_transform(df['tags'].values.astype('U')).toarray()
print(f"Created {vectorized.shape[1]:,} features from {vectorized.shape[0]:,} anime")

# Compute similarity matrix
print("Computing similarity matrix...")
sim = cosine_similarity(vectorized)

# Create both exact and case-insensitive title mappings
title_to_index = pd.Series(df.index, index=df['title']).drop_duplicates()
title_to_index_lower = pd.Series(df.index, index=df['title'].str.lower()).drop_duplicates()

print(f"Initialization complete in {time.time() - start_time:.2f}s")
print(f"Ready to serve {len(title_to_index):,} anime titles\n")


def recommend(title, top_n=5):
    """
    Get anime recommendations based on content similarity.
    
    Args:
        title: Anime title to find recommendations for
        top_n: Number of recommendations to return (default: 5)
    
    Returns:
        List of recommendation dictionaries with metadata and similarity scores
    """
    # Try exact match first, then case-insensitive
    index = None
    
    if title in title_to_index:
        index = title_to_index[title]
    elif title.lower() in title_to_index_lower:
        index = title_to_index_lower[title.lower()]
    
    if index is None:
        return []
    
    # Get similarity scores for all anime
    distances = list(enumerate(sim[index]))
    
    # Sort by similarity (highest first)
    distances.sort(reverse=True, key=lambda x: x[1])
    
    seen_titles = set()
    recommendations = []
    
    for idx, score in distances:
        # Skip the input anime itself
        if idx == index:
            continue
        
        anime_title = metadata.iloc[idx]['title']
        
        # Skip duplicates
        if anime_title in seen_titles:
            continue
        
        seen_titles.add(anime_title)
        
        # Build recommendation object
        rec = {
            "title": anime_title,
            "genre": metadata.iloc[idx]['genre'],
            "type": metadata.iloc[idx]['type'],
            "source": metadata.iloc[idx]['source'],
            "similarity": round(float(score), 4)
        }
        
        # Add optional metadata if available
        for col in ['score', 'episodes', 'aired', 'studio']:
            if col in metadata.columns:
                val = metadata.iloc[idx][col]
                if pd.notna(val):
                    rec[col] = val
        
        recommendations.append(rec)
        
        if len(recommendations) == top_n:
            break
    
    return recommendations


def search_titles(query, limit=20):
    """
    Search for anime titles containing the query string.
    Case-insensitive search.
    """
    query_lower = query.lower()
    matches = []
    
    for title in df['title'].dropna().values:
        if query_lower in str(title).lower():
            matches.append(str(title))
            if len(matches) >= limit:
                break
    
    return matches


def get_random(count=1):
    """Get random anime from the dataset."""
    count = min(max(1, count), 50)
    return df['title'].dropna().sample(n=count).tolist()