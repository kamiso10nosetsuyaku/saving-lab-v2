import os
import re
import csv
from datetime import datetime
from pathlib import Path

import tweepy
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GENERATED_CSV = BASE_DIR / "data" / "generated_posts.csv"
POSTED_CSV = BASE_DIR / "data" / "posted.csv"

X_API_KEY = os.getenv("X_API_KEY") or os.getenv("API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET") or os.getenv("API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET") or os.getenv("ACCESS_TOKEN_SECRET")


def clean_post(text, max_len=150):
    text = str(text).strip()
    text = text.replace("￥", "円").replace("〜", "～")
    text = re.sub(r"https?://\S+", "", text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)

    while len(text) > max_len and len(lines) > 1:
        lines.pop()
        text = "\n".join(lines)

    if len(text) > max_len:
        text = text[:max_len - 1] + "…"

    return text.strip()


def get_latest_generated_post():
    with open(GENERATED_CSV, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    latest = rows[-1]

    for key in ["post", "text", "content", "投稿"]:
        if key in latest and latest[key]:
            return latest[key]

    raise ValueError("投稿本文の列が見つかりません")


def save_posted(text, tweet_id):
    POSTED_CSV.parent.mkdir(exist_ok=True)
    file_exists = POSTED_CSV.exists()

    with open(POSTED_CSV, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["posted_at", "tweet_id", "text", "length", "lines"],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "posted_at": datetime.now().isoformat(timespec="seconds"),
            "tweet_id": tweet_id,
            "text": text,
            "length": len(text),
            "lines": text.count("\n") + 1,
        })


def post_to_x(text):
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )

    return client.create_tweet(text=text, user_auth=True)


if __name__ == "__main__":
    raw_text = get_latest_generated_post()
    post_text = clean_post(raw_text)

    print("投稿本文:")
    print(post_text)
    print("文字数:", len(post_text))
    print("行数:", post_text.count("\n") + 1)

    response = post_to_x(post_text)
    tweet_id = response.data["id"]

    save_posted(post_text, tweet_id)

    print("投稿成功")
    print("tweet_id:", tweet_id)