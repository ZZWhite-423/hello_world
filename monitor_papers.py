import feedparser
import os

# 定义搜索关键词：比色检测
# 你可以根据需要修改，比如 "colorimetric detection AND nanoparticles"
QUERY = 'abs:"colorimetric detection"'
URL = f'http://export.arxiv.org/api/query?search_query={QUERY}&sortBY=submittedDate&sortOrder=descending'

def get_latest_papers():
    feed = feedparser.parse(URL)
    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write("# 🔬 比色检测最新论文监控 (Latest Papers)\n\n")
        for entry in feed.entries[:10]: # 只取最新的10篇
            f.write(f"### [{entry.title}]({entry.link})\n")
            f.write(f"- **发布日期**: {entry.published}\n")
            f.write(f"- **摘要**: {entry.summary[:300]}...\n\n")

if __name__ == "__main__":
    get_latest_papers()
