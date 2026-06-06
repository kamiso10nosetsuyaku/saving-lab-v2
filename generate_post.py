from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import pandas as pd
import difflib
from datetime import datetime
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY が設定されていません")

api_key = api_key.replace("\n", "").replace("\r", "").replace(" ", "").replace('"', "").replace("'", "")

if api_key.startswith("OPENAI_API_KEY="):
    api_key = api_key.replace("OPENAI_API_KEY=", "")

client = OpenAI(api_key=api_key)

categories = [
    "診断型",
    "ランキング型",
    "年間損失換算型",
    "固定費削減型",
    "行動経済学型",
]

weekday = datetime.now().weekday()

category_map = {
    0: "診断型",
    1: "ランキング型",
    2: "年間損失換算型",
    3: "固定費削減型",
    4: "行動経済学型",
    5: "診断型",
    6: "ランキング型"
}

category = category_map[weekday]

条件：
・カテゴリに合う投稿を1つ作る
・100〜150文字
・6〜10行
・数字を多めに入れる
・投稿本文のみ出力
・根拠の弱い大きな金額は禁止
・有名人の名前は禁止
・引用形式は禁止
・ハイフンやダッシュ記号は禁止
・必ずオリジナル文章のみ出力
"""

last_error = None

for i in range(3):
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
            timeout=60,
        )
        post = response.output_text.strip()
        break
    except Exception as e:
        last_error = e
        print(f"OpenAI API接続失敗 {i + 1}/3: {e}")
        time.sleep(10)
else:
    raise last_error

char_count = len(post)
line_count = len(post.splitlines())

print("\n今日のカテゴリ：")
print(category)

print("\n今日の投稿：\n")
print(post)

print(f"\n文字数：{char_count}")
print(f"行数：{line_count}")
def is_similar_to_recent(post_text, csv_path, threshold=0.8):

    if not csv_path.exists():
        return False

    try:
        old_df = pd.read_csv(csv_path)

        if "post" not in old_df.columns:
            return False

        recent_posts = old_df["post"].dropna().tail(50)

        for old_post in recent_posts:

            score = difflib.SequenceMatcher(
                None,
                str(post_text),
                str(old_post)
            ).ratio()

            if score >= threshold:
                print(f"類似投稿検出: {score:.2f}")
                return True

        return False

    except Exception:
        return False
csv_path = BASE_DIR / "data" / "generated_posts.csv"
csv_path.parent.mkdir(exist_ok=True)

df = pd.DataFrame([{
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "category": category,
    "char_count": char_count,
    "line_count": line_count,
    "post": post,
    "status": "generated"
}])

if csv_path.exists() and csv_path.stat().st_size > 0:
    df.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
else:
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("\ngenerated_posts.csv に保存しました")