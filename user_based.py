
"""
About The Dataset

Ratings Data File Structure (ratings.csv)

All ratings are contained in the file ratings.csv. Each line of this file after the header row represents one rating of one movie by one user, and has the following format:

userId,movieId,rating,timestamp
The lines within this file are ordered first by userId, then, within user, by movieId.

Ratings are made on a 5-star scale, with half-star increments (0.5 stars - 5.0 stars).

Timestamps represent seconds since midnight Coordinated Universal Time (UTC) of January 1, 1970.


------------------------------------------------------------------------

Movies Data File Structure (movies.csv)

Movie information is contained in the file movies.csv. Each line of this file after the header row represents one movie, and has the following format:

movieId,title,genres
Movie titles are entered manually or imported from https://www.themoviedb.org/, and include the year of release in parentheses. Errors and inconsistencies may exist in these titles.

Genres are a pipe-separated list, and are selected from the following:

Action
Adventure
Animation
Children's
Comedy
Crime
Documentary
Drama
Fantasy
Film-Noir
Horror
Musical
Mystery
Romance
Sci-Fi
Thriller
War
Western
(no genres listed)


----------------------------------------------------------
"""

#Importing essential libraries.
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


#Importing Dataset

mov = pd.read_csv("data/movies.csv")
rate = pd.read_csv("data/ratings.csv")

#print("Columns of movies :",mov.columns)
#print("Columns of ratings :",rate.columns)

# Merging them on movieID col

df = pd.merge(mov,rate, on= 'movieId')
"""
df.head()
df.shape
df.describe()
df.isnull().sum()
print("Number of Users :", df['userId'].nunique())
print("Number of movies :", df['movieId'].nunique())
"""
#Transform the table where rows are userId and Title are columns and values are the ratings of the movie watched by the user


df_trans = pd.pivot_table(df,index = 'userId', columns = 'title', values= 'rating', fill_value = 0 , margins = False)
#df_trans

#df_trans.shape

#df_trans.head()

#checking for sparsity.
no_of_cells = df_trans.shape[0] * df_trans.shape[1] #rows * cols
no_non_zero = (df_trans != 0).sum().sum()
#print( "Number of cells in the table  : ", no_of_cells)
#print( "Number of Non-Zero cells in the table : ",int(no_non_zero) )

# SPARSITY % (mostly empty as not every user watch every movie )

sparsity = (1 - (no_non_zero/no_of_cells))*100
#print( "Pecentage of sparsity in the table : ", sparsity)

"""The user-item matrix is highly sparse, which is why collaborative filtering and matrix factorization techniques are designed to handle sparsity efficiently.
---
**Similarity Formula used :**

similarity(A,B)=cos(θ)=A⋅B​ / ∥A∥×∥B∥

each user column is reperesented as vectors
"""

# Creating Similarity Matrix

user_sim = cosine_similarity(df_trans)
df_sim = pd.DataFrame(user_sim, columns = df_trans.index, index = df_trans.index)

"""Greater the value of similarity -> Greater is the liking of movie watched by other user.

"""
#df_sim.head()
#df_sim.shape

"""Logic :
For a user_id,
Find similar users — get their similarity scores, sort them, exclude the user themselves.
Pick top K similar users .
Look at what movies those similar users rated highly.
Remove movies the target user has already watched.
Return the top N movie recommendations.

# checking with one user
"""

userId = 1

#print("User Id column\n",df_sim[userId])

sim_to_usr1 = df_sim[userId].sort_values(ascending =False)
sim_to_usr1 = sim_to_usr1.drop(userId)
#print(sim_to_usr1)

#sim_to_usr1.head()

# For K user

k = 10
top_k = sim_to_usr1.head(k)
#top_k

rating_by_sim_user= df_trans.loc[top_k.index]
#rating_by_sim_user

# Removing the movies the user already watched.
movie_usr1 = df_trans.loc[userId] #movies watched by userID = 1
#movie_usr1

unwatched = movie_usr1[movie_usr1 == 0].index
#unwatched

"""The Idea
For each unwatched movie:
score=∑(similarity[i] × rating[i] ) / ∑similarity[i]
This means: movies rated highly by very similar users get a higher score than movies rated highly by less similar users.
"""

#len(unwatched) # There are these number of unwatched movies which target user 1 hasn't watched yet.

# Now will find the ratings of these movies given by similar users and recommend it to user 1 to watch

sim_unwatched_ratings= rating_by_sim_user[unwatched]
#sim_unwatched_ratings

# Weighted score to sort movies with higher recommendations (Nr)
weighted_score = sim_unwatched_ratings.T.dot(top_k)

# Dr
top_k_sim_sum = top_k.sum()

final_movie_score = weighted_score / top_k_sim_sum

recommendations = final_movie_score.sort_values(ascending = False).head(10) # top 10 recommendations
#print("10 Movies for target user 1 \n\n", recommendations)

# Displaying the recommendation in clearner format

recommendations_df= pd.DataFrame(recommendations)
recommendations_df.columns = ['Ratings']
recommendations_df.index.name ='title'
recommendations_df = recommendations_df.reset_index()
recommendations_df

recommendations_df = recommendations_df.merge(df[['title', 'genres']].drop_duplicates(),on='title', how='left')
recommendations_df

"""
print("TOP 10 MOVIES RECOMMENDATIONS FOR USER_ID-1 ARE : \n\n")
print(recommendations_df.to_string())
"""
# Constructing the wrapper function

def get_recommendations(userId, k=10):

    # Step 1: Get similar users
    sim_to_usrId = df_sim[userId].sort_values(ascending =False)
    sim_to_usrId= sim_to_usrId.drop(userId)


    # Step 2: Pick top K similar users
    top_k = sim_to_usrId.head(k)

    # Step 3: Get their ratings
    rating_by_sim_user= df_trans.loc[top_k.index]


    # Step 4: Find unwatched movies
    # Removing the movies the user already watched.
    movie_usrId = df_trans.loc[userId] #movies watched by userID = 1
    unwatched = movie_usrId[movie_usrId == 0].index
    # Now will find the ratings of these movies given by similar users and recommend it to user 1 to watch

    sim_unwatched_ratings= rating_by_sim_user[unwatched]


    # Step 5: Score and rank movies
    # Weighted score to sort movies with higher recommendations (Nr)
    weighted_score = sim_unwatched_ratings.T.dot(top_k)

    # Dr
    top_k_sim_sum = top_k.sum()

    final_movie_score = weighted_score / top_k_sim_sum

    recommendations = final_movie_score.sort_values(ascending = False).head(k) # top k recommendations

    # Step 6: Return top N recommendations as DataFrame
    # Displaying the recommendation in clearner format

    recommendations_df= pd.DataFrame(recommendations)
    recommendations_df.columns = ['Ratings']
    recommendations_df.index.name ='title'
    recommendations_df =recommendations_df.reset_index() # for getting the serial no. in order


    recommendations_df = recommendations_df.merge(df[['title', 'genres']].drop_duplicates(),on='title', how='left')
    

    return recommendations_df

"""
print(get_recommendations(29))

print(get_recommendations(1))

print(get_recommendations(1,20))
"""

