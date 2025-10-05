import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_textblob_sentiment_polarity(text):
    # Get the TextBlog sentiment polarity of the message text
    if pd.isna(text) or (isinstance(text, str) and text.strip() == ''):
        return None
    tb = TextBlob(str(text))
    return tb.sentiment.polarity

def get_vader_sentiment_compound(text):
    if pd.isna(text) or (isinstance(text, str) and text.strip() == ''):
        return None
    vader = SentimentIntensityAnalyzer()
    sentiment = vader.polarity_scores(str(text))
    return sentiment.get('compound')

def set_textblob_scores(df: pd.DataFrame):
    # Get sentiment polarity of message_body and add to DataFrame
    df['tb_polarity'] = df['message_body'].apply(get_textblob_sentiment_polarity)

def set_vader_scores(df: pd.DataFrame):  
        # Get sentiment compound of message_body and add to DataFrame
    df['vader_compound'] = df['message_body'].apply(get_vader_sentiment_compound)
