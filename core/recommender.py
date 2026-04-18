import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .models import Restaurant

def get_recommendations(target_name):
    qs = Restaurant.objects.all().values('id', 'name', 'cuisine', 'features', 'description')
    df = pd.DataFrame(qs)

    if df.empty or len(df) < 2: return []

    df['profile'] = df['cuisine'] + " " + df['features'] + " " + df['description']
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['profile'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    try:
        idx = df[df['name'] == target_name].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
   
        top_indices = [i[0] for i in sim_scores[1:4]]
   
        recommended_ids = df.iloc[top_indices]['id'].tolist()
        return Restaurant.objects.filter(id__in=recommended_ids)
    except:
        return []