from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import pandas as pd
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

categories = [
    "節約ノウハウ",
    "節約ノウハウ",
    "行動経済学・研究系",
    "行動経済学・研究系",
    "診断型"
]

category = random.choice(categories)

with open("prompts/daily_prompt.txt", "r", encoding="utf-8") as f:
    base_prompt = f.read()

prompt = base_prompt + f"""

今日のカテゴリ：
{category}

条件：
・カテゴリに合う投稿を1つ作る
・100〜170文字
・8〜16行
・数字を多めに入れる
・投稿本文だけ出力\n・月の節約額は500円から30000円まで\n・根拠の弱い大きな金額は禁止\n・有名人の名言は禁止\n・引用形式は禁止\n・ハイフンやダッシュ記号は禁止\n・必ずオリジナル文章のみ出力
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

df = pd.DataFrame([{
    "created_at": datetime.now(),
    "category": category,
    "char_count": char_count,
    "line_count": line_count,
    "post": post,
    "status": "generated"
}])

csv_path = "data/generated_posts.csv"

if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
    df.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
else:
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("\ngenerated_posts.csv に保存しました")