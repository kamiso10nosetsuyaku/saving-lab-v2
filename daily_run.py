import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_script(script_name: str):
    print(f"\n=== {script_name} 実行 ===")
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / script_name)],
        cwd=BASE_DIR,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} で失敗しました")


if __name__ == "__main__":
    run_script("generate_post.py")
    run_script("post_to_x.py")

    print("\n完了：生成 → CSV保存 → X投稿 → posted.csv記録")