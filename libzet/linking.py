from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def create_suggested_links(zettels):
    # Extract titles and content from zettels
    titles = [zettel["title"] for zettel in zettels]
    content = [zettel["content"] for zettel in zettels]

    # Use TF-IDF to vectorize the content of each zettel
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(content)

    # Compute pairwise cosine similarities between zettels
    cosine_similarities = np.dot(X, X.T)

    # Create a dictionary of suggested links for each zettel
    suggested_links = {}
    for i, zettel in enumerate(zettels):
        title = zettel["title"]
        sim_scores = list(enumerate(cosine_similarities[i]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Exclude self-similarity
        zettel_indices = [i[0] for i in sim_scores]
        zettel_titles = [titles[j] for j in zettel_indices]
        suggested_links[title] = zettel_titles

    return suggested_links
