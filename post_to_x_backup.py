import os
import pandas as pd
import tweepy
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

csv_path = "data/generated_posts.csv"
posted_path = "data/posted.csv"

api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

if not all([api_key, api_secret, access_token, access_token_secret]):
    raise ValueError("X APIキーが.envに設定されていません")

df = pd.read_csv(csv_path)

target = df[df["status"] == "generated"].tail(1)

if target.empty:
    print("投稿対象がありません")
    exit()

row = target.iloc[0]
post_text = row["post"]

client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

response = client.create_tweet(text=post_text, user_auth=True)

tweet_id = response.data["id"]

print("Xに投稿しました")
print(f"tweet_id: {tweet_id}")

posted_df = pd.DataFrame([{
    "posted_at": datetime.now(),
    "tweet_id": tweet_id,
    "category": row.get("category", ""),
    "char_count": row.get("char_count", ""),
    "line_count": row.get("line_count", ""),
    "post": post_text,
    "status": "posted"
}])

if os.path.exists(posted_path) and os.path.getsize(posted_path) > 0:
    posted_df.to_csv(posted_path, mode="a", header=False, index=False, encoding="utf-8-sig")
else:
    posted_df.to_csv(posted_path, index=False, encoding="utf-8-sig")

df.loc[target.index, "status"] = "posted"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("posted.csv に記録しました")