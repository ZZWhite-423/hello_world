import feedparser
import os
import time
from urllib.parse import quote
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. 配置和初始化保持不变
API_KEY = os.environ.get("DOUBAO_API_KEY")
ENDPOINT_ID = os.environ.get("DOUBAO_ENDPOINT_ID")

if API_KEY and ENDPOINT_ID:
    client = OpenAI(api_key=API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3")
else:
    client = None

KEYWORD = 'abs:"colorimetric detection"'
URL = f'http://export.arxiv.org/api/query?search_query={quote(KEYWORD)}&sortBY=submittedDate&sortOrder=descending'

MUST_READ_KEYWORDS = {"gold": 2, "silver": 2, "sensitivity": 3, "LOD": 3, "Fe2O4": 5}
HISTORY_FILE = "history.txt"  # 🌟 新增：机器人的记忆小本子

def get_score(title, summary):
    score = 0
    text = (title + " " + summary).lower()
    for kw, weight in MUST_READ_KEYWORDS.items():
        if kw.lower() in text:
            score += weight
    return score

def translate_text(text):
    if not client: return "⚠️ 未配置豆包 API，跳过翻译。"
    try:
        response = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[
                {"role": "system", "content": "你是一个专业的材料化学领域的翻译专家。"},
                {"role": "user", "content": f"请翻译以下摘要：\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"翻译失败: {e}"

def send_email(content):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    if not all([sender, password, receiver]): return

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "🔔 科研早报：比色检测最新文献 (去重版)"
    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465) # 163邮箱请换成 smtp.163.com
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("✅ 发现新文献，邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

# 🌟 新增：读取记忆
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set() # 如果没有本子，就建一个空的集合
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

# 🌟 新增：保存记忆
def save_history(history_set):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for link in history_set:
            f.write(f"{link}\n")

def get_latest_papers():
    feed = feedparser.parse(URL)
    history = load_history()
    new_papers = []
    
    # 🌟 核心去重逻辑
    for entry in feed.entries:
        if entry.link in history:
            continue # 如果本子上记过了，直接跳过！
        
        new_papers.append(entry)
        history.add(entry.link) # 记到本子上
        
        if len(new_papers) >= 5: # 每次最多只处理 5 篇新的
            break
            
    # 🌟 静默拦截：如果没有新论文，直接下班
    if not new_papers:
        print("📭 今天没有关于比色检测的新论文，代码静默退出。")
        return

    md_content = "# 🔬 比色检测最新文献 (已去重)\n\n"
    for entry in new_papers:
        score = get_score(entry.title, entry.summary)
        md_content += f"### [{entry.title}]({entry.link}) | 得分: {score}\n"
        md_content += f"**🤖 AI 摘要**：\n> {translate_text(entry.summary)}\n\n---\n\n"
        time.sleep(2)

    with open("Latest_Papers.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    save_history(history) # 保存本子
    send_email(md_content)

if __name__ == "__main__":
    get_latest_papers()
