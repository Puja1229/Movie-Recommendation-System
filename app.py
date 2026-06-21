import streamlit as st
from user_based import *
from item_based import get_movie_recommendations, df_sim

st.title("MOVIE RECOMMEDATION SYSTEM")


tab1, tab2 = st.tabs(['User Based',' Item Based'])

with tab1 :
    st.subheader(" Get Recommendations based on Similar Users")

    user_Id = st.selectbox("Select your User Id", df_trans.index)

    if st.button("Get Recommendations", key='user') :
        recommendation_df = get_recommendations(user_Id)
        st.success(f" Top 10 Recommendations for User {user_Id}")
        st.dataframe(recommendation_df)
  

with tab2:
    st.subheader("Get Recommendations Based on a Movie You Like")
    movie_name = st.selectbox("Select a Movie", df_sim.index)

    if st.button("Get Recommendations", key='movie'):
        recommendations_df = get_movie_recommendations(movie_name)
        if recommendations_df is None:
            st.error("Movie not found!")
        else:
            st.success(f"Top 10 Movies Similar to {movie_name}")
            st.dataframe(recommendations_df)

    
