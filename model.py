import snscrape.modules.twitter as sn
import re
import openai
from flask import abort, jsonify


# Set your OpenAI API key
openai.api_key = "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"

def fetch_tweet(query, num_tweets=10, tweet_len=150):
    tweets = []
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)

    def remove_emojis(data):
        return re.sub(emoj, '', data)

    def contains_non_english_words(data):
        for x in data.split(" "):
            if not re.search('[a-zA-Z0-9]', x):
                return True
        return False

    counts = 0

    try:
        scraper = sn.TwitterUserScraper(query)
        print(scraper.entity == None)
        if scraper.entity == None:
            abort(400, 'User not found for given username = '+query)

    except ValueError:
       abort(400, 'User not found for given username = '+query)

    try:
        for tweet in sn.TwitterProfileScraper(query).get_items():
            if counts == num_tweets:
                break
            else:
                if not hasattr(tweet, 'content'):
                    continue
                if contains_non_english_words(tweet.content):
                    continue
                if re.search(r'https?:\/\/\S+|www?\S+', tweet.content):
                    continue
                if len(tweet.content) > tweet_len:
                    tweet.content = re.sub(r'https?:\/\/\S+|www?\S+', '', tweet.content)
                    tweet.content = re.sub(r'[@|#|.|;|!|&|:|-]', ' ', tweet.content)
                    tweet.content = remove_emojis(tweet.content)
                    tweets.append(tweet.content[:tweet_len])
                    counts += 1

    except:
        # print("user not ffound")
         abort(400, 'User not found for given username = '+query)

    return tweets


def classify_tweets(tweets, labels, query):
    prompt = "Classify the occupation of a Twitter user: "+query+"  based on their recent tweets:\n\n"
    for tweet in tweets:
        prompt += tweet + "\n"

    prompt += "Occupations: " + ', '.join(labels) + "\n"
    prompt += "Note: Only single-word occupations from the above list are available.\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.8,
    )

    predicted_occupation = ""
    prediction = response.choices[0].text.strip()
    print(response)
    for label in labels:
        if label.lower() in prediction.lower():
            predicted_occupation = label
            break

    if not predicted_occupation:
        predicted_occupation = "Occupation not predicted"

    return predicted_occupation


def get_prediction(query, num_tweets=10, tweet_len=150):
    labels = [
    "Politician",
    "Movie Star",
    "Entrepreneur",
    "Software Engineer",
    "Defence",
    "Attorney",
    "Chartered Accountant",
    "Cricketer",
    "Cricket Journalist",
    "Journalist",
    "Sports",
    "Professor",
    "Author",
    "Chef",
    "Data Analytics",
    "Doctor",
    "Musician",
    "Engineer",
    # "Architect",
    "Pilot",
    "Human Resources Manager",
    # "Social Media influencers"
    ]
    tweets = fetch_tweet(query, num_tweets, tweet_len)

    if(len(tweets) < num_tweets):
        abort(400, "User shoud have manimum "+ str(num_tweets) +" tweets with length "+str(tweet_len))

    occupation = classify_tweets(tweets, labels, query)
    return jsonify({
        "prdiction"  : occupation,
        "tweets" : tweets
    })


# # Example usage:
# search_query = "iamsrk"


# predicted_occupation = get_prediction(search_query)
# print("Predicted occupation:", predicted_occupation)
