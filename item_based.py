import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np 
import requests


# Load the dataset 

movies = pd.read_csv("data/movies.csv")
ratings = pd.read_csv("data/ratings.csv")
df = pd.merge(movies,ratings, on = 'movieId')
df['title'] = df['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
#print(df.head())

#Interaction Matrix
df_transform = pd.pivot_table(df, index = 'title', columns ='userId',values = 'rating', fill_value = 0)
#print(df_transform.head())

#Creating cosine similarity matrix
sim_matrix = cosine_similarity(df_transform)

df_sim = pd.DataFrame(sim_matrix, index = df_transform.index, columns = df_transform.index)

def get_movie_recommendations(movie_name, k=10):
    if movie_name not in df_sim.index:
        return None
    #getting the similar movies

    sim_movies = df_sim[movie_name].sort_values(ascending = False)
    sim_movies = sim_movies.drop(movie_name)
    # top k 
    top_k = sim_movies.head(k)

    # displaying it 

    recommendation_df = pd.DataFrame(top_k)
    recommendation_df.index.name = 'title'
    recommendation_df.columns = ['Similarity_score']
    recommendation_df = recommendation_df.reset_index()

    #Add genres
    recommendation_df = recommendation_df.merge(df[['title','genres']].drop_duplicates(), on = 'title', how= 'left')

    return recommendation_df


#print(get_movie_recommendations('Sabrina',10))

