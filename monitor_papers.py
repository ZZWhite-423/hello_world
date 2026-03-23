import feedparser
import os
import time
from urllib.parse import quote
from openai import OpenAI

# 配置豆包大模型 (火山引擎)
API_KEY = os.environ.get("DOUBAO_API_KEY")
ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID")

# 初始化客户端，指向火山引擎的服务器
if API_KEY and ENDPOINT_ID:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
else:
    client = None

# 1. 设置监控关键词
KEYWORD = 'abs:"colorimetric detection"'
QUERY = quote(KEYWORD)
URL = f'http://export.arxiv.org/api/query?search_query={QUERY}&sortBY=submittedDate&sortOrder=descending'

# 2. 定义“必读”关键词及其权重
MUST_READ_KEYWORDS = {
    "gold": 2, "silver": 2, "sensitivity": 3, "LOD": 3, "Fe2O4": 5
}

def get_score(title, summary):
    score = 0
    text = (title + " " + summary).lower()
    for kw, weight in MUST_READ_KEYWORDS.items():
        if kw.lower() in text:
            score += weight
    return score

def translate_text(text):
    if not client:
        return "⚠️ 未配置豆包 API 环境变量，跳过翻译。"
    try:
        response = client.chat.completions.create(
            model=ENDPOINT_ID, # 这里传入的是 ep- 开头的接入点 ID
            messages=[
                {"role": "system", "content": "你是一个专业的材料化学与分析化学领域的翻译专家。"},
                {"role": "user", "content": f"请将以下学术论文摘要翻译成流畅专业的中文：\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"豆包翻译失败: {e}"

def get_latest_papers():
    feed = feedparser.parse(URL)
    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write("# 🔬 比色检测最新论文监控 (豆包 AI 翻译版)\n\n")
        f.write("> 自动更新于: 2026-03-23 | 标注 🔥 为高匹配度论文\n\n---\n\n")
        
        # 抓取前 5 篇进行翻译
        for entry in feed.entries[:5]:
            score = get_score(entry.title, entry.summary)
            badge = " 🔥 [重点推荐]" if score >= 5 else (" ⭐ [建议阅读]" if score >= 2 else "")
            
            f.write(f"### {badge} [{entry.title}]({entry.link})\n")
            f.write(f"- **匹配得分**: {score}\n")
            f.write(f"- **发布日期**: {entry.published}\n\n")
            
            f.write("<details>\n<summary>展开查看英文原摘要</summary>\n\n")
            f.write(f"{entry.summary}\n\n</details>\n\n")
            
            f.write(f"**🤖 豆包 AI 中文翻译**：\n")
            zh_summary = translate_text(entry.summary)
            f.write(f"> {zh_summary}\n\n---\n\n")
            
            # 给大模型喘口气的时间
            time.sleep(2)

if __name__ == "__main__":
    get_latest_papers()
