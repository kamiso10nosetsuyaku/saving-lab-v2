from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

categories = [
    "診断型",
    "ランキング型",
    "年間損失換算型",
    "固定費削減型",
    "行動経済学型",
]

category = random.choice(categories)

with open(BASE_DIR / "prompts" / "daily_prompt.txt", "r", encoding="utf-8") as f:
    base_prompt = f.read()

prompt = base_prompt + f"""

今日のカテゴリ：
{category}

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

response = client.responses.create(
    model="gpt-5-mini",
    input=prompt
)

post = response.output_text.strip()

char_count = len(post)
line_count = len(post.splitlines())

print("\n今日のカテゴリ：")
print(category)

print("\n今日の投稿：\n")
print(post)

print(f"\n文字数：{char_count}")
print(f"行数：{line_count}")

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