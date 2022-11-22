import csv
import pickle
from pathlib import Path

from PIL import Image
import streamlit as st
from textblob import TextBlob
import pandas as pd
import altair as alt
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import streamlit_authenticator as stauth  # pip install streamlit-authenticator


@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

# --- USER AUTHENTICATION ---
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["admin"]

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    def main():
        st.title("Sentiment Analysis NLP App Bahasa Indonesia")
        st.subheader("Streamlit Projects")

        image = Image.open('indonesia.png')
        st.image(image, caption='Indonesia')
    
        menu = ["Home", "Twitter", "About"]
        authenticator.logout("Logout", "sidebar")
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Home":
            st.subheader("Home")
            with st.form("nlpForm"):
                raw_text = st.text_area("Masukan Text disini")
                submit_button = st.form_submit_button(label='Analyze')

                # layout
                col1,col2 = st.columns(2)
                if submit_button:

                    with col1:
                        st.info("Hasil")

                        analysis = TextBlob(raw_text)
                        an = analysis.translate(from_lang='id', to='en')
                        sentiment = an.sentiment

                        st.write(sentiment)

                        # Emoji
                        if sentiment.polarity > 0:
                            st.markdown("Sentiment:: Positif 😊 ")
                        elif sentiment.polarity < 0:
                            st.markdown("Sentiment:: Negatif 😡 ")
                        else:
                            st.markdown("Sentiment:: Netral 😐 ")

                        # DataFrame
                        result_df = convert_to_df(sentiment)
                        st.dataframe(result_df)

                        # Vizualization
                        c = alt.Chart(result_df).mark_bar().encode(
                            x='metric',
                            y='value',
                            color='metric')
                        st.altair_chart(c,use_container_width=True)

                    with col2:
                        st.info("Hasil")

                        token_sentiments = anlyze_token_sentiment(an)
                        st.write(token_sentiments)

        elif choice == "Twitter":
            st.header("Crawling Twitter")
            BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAKnQigEAAAAAn70vJe3M2UMaL1ghcEi3pp42n2U%3Dnv3Hn3mUkIFSo3N9zPN2fqbrymnGmxOy2wBmGRqS2MG4PLU2y6'
            with st.form ("text yang dicari"):
                query = st.text_area("Masukan keyword")
                tweet_count = st.slider("Masukan jumlah tweet: ", 10,100)

                submit_button2 = st.form_submit_button (label='Cari')
                if submit_button2:
                    # Masukkan Twitter Token API
                    client = tweepy.Client(bearer_token=BEARER_TOKEN)
                    # Query pencarian
                    hasil = client.search_recent_tweets(query=query, max_results=tweet_count, tweet_fields=['created_at', 'lang'], expansions= ['author_id'])
                    users = {u['id']: u for u in hasil.includes['users']}
                    t = []
                    u = []
                    i = []
                    s = []

                    #menambahkan tweet ke array
                    for tweet in hasil.data:
                        user = users[tweet.author_id]
                        sentiment = TextBlob(tweet.text).sentiment
                            
                        if sentiment.polarity > 0:
                                result = "Positive 😊 "
                        elif sentiment.polarity < 0:
                                result = "Negative 😡 "
                        else:
                                result = "Neutral 😐 "

                        i.append(tweet.id)
                        u.append(user.username)
                        t.append(tweet.text)
                        s.append(result)
            
                    #menampilkan ke dataframe
                    dictTweets = {"id":i,"username":u, "text":t, "Sentiment":s}
                    df = pd.DataFrame(dictTweets,columns=["id", "username", "Sentiment", "text"])
                    df

                else:
                    st.subheader("Tentang")

    def convert_to_df(sentiment):
        sentiment_dict = {'polarity':sentiment.polarity,'subjectivity':sentiment.subjectivity}
        sentiment_df = pd.DataFrame(sentiment_dict.items(),columns=['metric','value'])
        return sentiment_df

    def anlyze_token_sentiment(docx):
        analyzer = SentimentIntensityAnalyzer()
        pos_list = []
        neg_list = []
        neu_list = []
        for i in docx.split():
            res = analyzer.polarity_scores(i)['compound']
            if res > 0.1:
                pos_list.append(i)
                pos_list.append(res)

            if res <= -0.1:
                neg_list.append(i)
                neg_list.append(res)

            else:
                neu_list.append(i)

        result = {'positives':pos_list,'negtives':neg_list,'neutral':neu_list}
        return result
    if __name__ == '__main__':
        main()