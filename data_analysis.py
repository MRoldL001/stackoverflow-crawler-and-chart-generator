import os
from collections import Counter

import jieba
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud

DATA_FILE = "data/stackoverflow_questions.csv"
OUT_DIR = "output"
FONT_FILE = "C:/Windows/Fonts/msyh.ttc"
PERIOD_NAMES = {"hot": "\u70ed\u95e8\u95ee\u9898", "active": "\u6d3b\u8dc3\u95ee\u9898", "newest": "\u6700\u65b0\u95ee\u9898"}
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "into", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "with", "your", "you", "can", "could", "would", "should",
    "do", "does", "did", "doing", "using", "use", "get", "getting",
    "make", "made", "new", "one", "two", "way", "ways", "work", "working",
    "works", "still", "also", "just", "like", "really", "best", "better",
    "between", "how", "what", "why", "when", "where", "which", "who",
    "not", "error", "problem", "problems", "question", "questions", "help",
    "please", "issue", "issues", "solution", "solutions", "possible",
    "example", "examples",
}
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def make_words(data):
    # 统计词频
    result = Counter()
    for text in (data["title"].fillna("") + " " + data["tags"].fillna("")).astype(str):
        one_question = set()
        for word in jieba.lcut(text):
            word = word.strip().lower()
            if len(word) > 1 and word not in STOP_WORDS:
                one_question.add(word)
        result.update(one_question)
    return result


def save_bar(counter, title, filename, color, out_dir):
    items = counter.most_common(15)
    plt.figure(figsize=(10, 6))
    plt.bar([x[0] for x in items], [x[1] for x in items], color=color)
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, filename), dpi=150)
    plt.close()


def save_pie(counter, title, filename, out_dir):
    items = counter.most_common(10)
    plt.figure(figsize=(8, 8))
    plt.pie([x[1] for x in items], labels=[x[0] for x in items], autopct="%.1f%%")
    plt.title(title)
    plt.savefig(os.path.join(out_dir, filename), dpi=150)
    plt.close()


def make_long_image(out_dir):
    # 拼接长图
    files = [("\u95ee\u9898\u5173\u952e\u8bcd\u8bcd\u4e91", "\u8bcd\u4e91.png"), ("\u95ee\u9898\u5173\u952e\u8bcd\u8bcd\u9891\u67f1\u72b6\u56fe", "\u8bcd\u9891\u67f1\u72b6\u56fe.png"), ("\u95ee\u9898\u5173\u952e\u8bcd\u8bcd\u9891\u997c\u56fe", "\u8bcd\u9891\u997c\u56fe.png"), ("\u6280\u672f\u6807\u7b7e\u67f1\u72b6\u56fe", "\u6280\u672f\u6807\u7b7e\u67f1\u72b6\u56fe.png"), ("\u6280\u672f\u6807\u7b7e\u997c\u56fe", "\u6280\u672f\u6807\u7b7e\u997c\u56fe.png")]
    font = ImageFont.truetype(FONT_FILE, 32)
    blocks = []
    for title, filename in files:
        image = Image.open(os.path.join(out_dir, filename)).convert("RGB")
        image.thumbnail((1120, 700))
        block = Image.new("RGB", (1200, image.height + 135), "white")
        ImageDraw.Draw(block).text((40, 20), title, fill="black", font=font)
        block.paste(image, ((1200 - image.width) // 2, 100))
        blocks.append(block)
    result = Image.new("RGB", (1200, sum(x.height for x in blocks)), "white")
    top = 0
    for block in blocks:
        result.paste(block, (0, top))
        top += block.height
    result.save(os.path.join(out_dir, "\u5206\u6790\u957f\u56fe.png"))


def analyze_period(data, period):
    # 分析一个时间段
    name = PERIOD_NAMES[period]
    out_dir = os.path.join(OUT_DIR, name)
    os.makedirs(out_dir, exist_ok=True)
    words = make_words(data)
    save_bar(words, name + "\u5173\u952e\u8bcd\u8bcd\u9891\u67f1\u72b6\u56fe", "\u8bcd\u9891\u67f1\u72b6\u56fe.png", "steelblue", out_dir)
    save_pie(words, name + "\u5173\u952e\u8bcd\u8bcd\u9891\u997c\u56fe", "\u8bcd\u9891\u997c\u56fe.png", out_dir)
    tags = Counter(" ".join(data["tags"].fillna("")).split())
    save_bar(tags, name + "\u6280\u672f\u6807\u7b7e\u67f1\u72b6\u56fe", "\u6280\u672f\u6807\u7b7e\u67f1\u72b6\u56fe.png", "darkorange", out_dir)
    save_pie(tags, name + "\u6280\u672f\u6807\u7b7e\u997c\u56fe", "\u6280\u672f\u6807\u7b7e\u997c\u56fe.png", out_dir)
    WordCloud(width=1000, height=600, background_color="white").generate_from_frequencies(words).to_file(os.path.join(out_dir, "\u8bcd\u4e91.png"))
    make_long_image(out_dir)


def main():
    # 读取数据
    data = pd.read_csv(DATA_FILE).drop_duplicates(subset=["period", "title"])
    data["tags"] = data["tags"].fillna("")
    data.to_csv("data/stackoverflow_questions_clean.csv", index=False, encoding="utf-8-sig")
    for period in ["hot", "active", "newest"]:
        part = data[data["period"] == period]
        if len(part) > 0:
            analyze_period(part, period)
    print("分析完成")


if __name__ == "__main__":
    main()
