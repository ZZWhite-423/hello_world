import feedparser
import os
from urllib.parse import quote  # 导入这个工具来处理空格

# 定义搜索关键词
KEYWORD = 'abs:"colorimetric detection"'
# 对关键词进行编码，把空格变成 %20
QUERY = quote(KEYWORD)

URL = f'http://export.arxiv.org/api/query?search_query={QUERY}&sortBY=submittedDate&sortOrder=descending'

def get_latest_papers():
    # 后面的代码保持不变...
    feed = feedparser.parse(URL)
    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write("# 🔬 比色检测最新论文监控 (Latest Papers)\n\n")
        for entry in feed.entries[:10]: # 只取最新的10篇
            f.write(f"### [{entry.title}]({entry.link})\n")
            f.write(f"- **发布日期**: {entry.published}\n")
            f.write(f"- **摘要**: {entry.summary[:300]}...\n\n")

if __name__ == "__main__":
    get_latest_papers()
