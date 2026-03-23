import feedparser
import os
from urllib.parse import quote

# 1. 设置监控关键词
KEYWORD = 'abs:"colorimetric detection"'
QUERY = quote(KEYWORD)
URL = f'http://export.arxiv.org/api/query?search_query={QUERY}&sortBY=submittedDate&sortOrder=descending'

# 2. 定义“必读”关键词及其权重（你可以根据实验需求修改）
MUST_READ_KEYWORDS = {
    "gold": 2,          # 金纳米粒子相关
    "silver": 2,        # 银相关
    "sensitivity": 3,   # 灵敏度提升
    "limit of detection": 3, # 检测限
    "LOD": 3,
    "smartphone": 2,    # 智能手机便携检测
    "paper-based": 2,   # 纸基分析
    "Fe2O4": 5          # 重点：和你现在的铁酸盐实验高度相关！
}

def get_score(title, summary):
    score = 0
    text = (title + " " + summary).lower()
    for kw, weight in MUST_READ_KEYWORDS.items():
        if kw.lower() in text:
            score += weight
    return score

def get_latest_papers():
    feed = feedparser.parse(URL)
    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write("# 🔬 比色检测最新论文监控 (带有权重筛选)\n\n")
        f.write("> 自动更新于: 2026-03-23 | 标注 🔥 为高匹配度论文\n\n---\n\n")
        
        for entry in feed.entries[:15]:
            score = get_score(entry.title, entry.summary)
            # 根据得分加标记
            badge = " 🔥 [重点推荐]" if score >= 5 else (" ⭐ [建议阅读]" if score >= 2 else "")
            
            f.write(f"### {badge} [{entry.title}]({entry.link})\n")
            f.write(f"- **匹配得分**: {score}\n")
            f.write(f"- **发布日期**: {entry.published}\n")
            f.write(f"- **摘要**: {entry.summary[:350]}...\n\n")

if __name__ == "__main__":
    get_latest_papers()
