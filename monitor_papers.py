import feedparser
import os
import time
from urllib.parse import quote
from openai import OpenAI
import urllib.request
import json

# 配置豆包大模型 (火山引擎)
API_KEY = os.environ.get("DOUBAO_API_KEY")
ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID")

if API_KEY and ENDPOINT_ID:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
else:
    client = None

KEYWORD = 'abs:"colorimetric detection"'
QUERY = quote(KEYWORD)
URL = f'http://export.arxiv.org/api/query?search_query={QUERY}&sortBY=submittedDate&sortOrder=descending'

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
        return "⚠️ 未配置豆包 API，跳过翻译。"
    try:
        response = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[
                {"role": "system", "content": "你是一个专业的材料化学与分析化学领域的翻译专家。"},
                {"role": "user", "content": f"请将以下学术论文摘要翻译成流畅专业的中文：\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"豆包翻译失败: {e}"

# 新增：微信推送函数
def push_to_wechat(content):
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("⚠️ 未找到 PUSHPLUS_TOKEN，跳过微信推送。")
        return
        
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": "🔔 科研早报：比色检测最新文献",
        "content": content,
        "template": "markdown" # 告诉微信用 Markdown 格式漂亮地排版
    }
    try:
        body = json.dumps(data).encode(encoding='utf-8')
        req = urllib.request.Request(url=url, data=body, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        print("✅ 微信推送成功！")
    except Exception as e:
        print(f"❌ 微信推送失败: {e}")

def get_latest_papers():
    feed = feedparser.parse(URL)
    
    # 我们先用一个变量把所有的内容收集起来
    md_content = "# 🔬 比色检测最新论文监控 (豆包 AI 翻译版)\n\n"
    md_content += "> 自动更新于: GitHub Actions | 标注 🔥 为高匹配度论文\n\n---\n\n"
    
    for entry in feed.entries[:5]:
        score = get_score(entry.title, entry.summary)
        badge = " 🔥 [重点推荐]" if score >= 5 else (" ⭐ [建议阅读]" if score >= 2 else "")
        
        md_content += f"### {badge} [{entry.title}]({entry.link})\n"
        md_content += f"- **匹配得分**: {score}\n"
        md_content += f"- **发布日期**: {entry.published}\n\n"
        
        md_content += f"**🤖 AI 中文摘要**：\n"
        zh_summary = translate_text(entry.summary)
        md_content += f"> {zh_summary}\n\n---\n\n"
        
        time.sleep(2)

    # 1. 写入 GitHub 本地仓库
    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    # 2. 发送到你的微信
    push_to_wechat(md_content)

if __name__ == "__main__":
    get_latest_papers()
