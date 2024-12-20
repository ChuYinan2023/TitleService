from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import zhipuai
from zhipuai import ZhipuAI  # 导入 ZhipuAI 客户端
import os
import logging

# 直接在代码中设置环境变量
os.environ['ZHIPUAI_API_KEY'] = 'e8d5a4cd0a1d496de21ed08c64268a85.H8YYYahnU4CRGq8X'

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量读取API Key
zhipuai.api_key = os.getenv('ZHIPUAI_API_KEY', '')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_tags_and_keywords(text):
    try:
        # 使用 ZhipuAI 客户端
        client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY', ''))
        
        response = client.chat.completions.create(
            model="glm-4v-flash",  # 或者 "glm-4v-flash"
            messages=[
                {
                    "role": "user", 
                    "content": f"请为以下文本生成5个最相关的标签和5个最相关的关键词。文本内容：{text}。请以以下格式返回：\n标签：标签1、标签2、标签3、标签4、标签5\n关键词：关键词1、关键词2、关键词3、关键词4、关键词5"
                }
            ],
            top_p=0.7,
            temperature=0.9,
            max_tokens=256
        )
        
        # 打印完整的响应以便调试
        logging.info("完整的AI响应: %s", response)
        result_text = response.choices[0].message.content
        logging.info("AI响应内容: %s", result_text)
        
        # 更健壮的解析方法
        tags = []
        keywords = []
        
        for line in result_text.split('\n'):
            line = line.strip()
            if line.startswith('标签：'):
                tags = [tag.strip() for tag in line.replace('标签：', '').split('、') if tag.strip()]
            elif line.startswith('关键词：'):
                keywords = [keyword.strip() for keyword in line.replace('关键词：', '').split('、') if keyword.strip()]
        
        # 如果解析失败，尝试更灵活的方法
        if not tags or not keywords:
            # 尝试从整个文本中提取
            parts = result_text.split('\n')
            for part in parts:
                if '标签' in part and not tags:
                    tags = [tag.strip() for tag in part.split('：')[-1].split('、') if tag.strip()]
                if '关键词' in part and not keywords:
                    keywords = [keyword.strip() for keyword in part.split('：')[-1].split('、') if keyword.strip()]
        
        # 限制数量为5个
        tags = tags[:5]
        keywords = keywords[:5]
        
        logging.info("最终标签: %s", tags)
        logging.info("最终关键词: %s", keywords)
        
        return tags, keywords
    
    except Exception as e:
        logging.error("AI生成标签和关键词时出错: %s", e)
        return [], []

def generate_summary(text, max_length=300):
    try:
        # 检查输入文本是否为空或过短
        if not text or len(text) < 10:
            logging.warning("输入文本过短，无法生成摘要")
            return ""

        # 使用 ZhipuAI 客户端生成摘要
        client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY', ''))
        
        response = client.chat.completions.create(
            model="glm-4v-flash",
            messages=[
                {
                    "role": "user", 
                    "content": f"""请为以下文本生成一个简洁精炼的摘要。要求：
1. 保留核心信息和主要观点
2. 摘要长度控制在{max_length}个字符以内
3. 使用清晰、简洁的语言
4. 如果文本过短或无实质内容，返回空字符串

文本内容：{text}"""
                }
            ],
            top_p=0.7,
            temperature=0.9,
            max_tokens=256
        )
        
        # 获取摘要内容
        summary = response.choices[0].message.content.strip()
        
        # 确保摘要不超过指定长度
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        logging.info(f"生成的摘要: {summary}")
        return summary
    
    except Exception as e:
        logging.error(f"生成摘要时出错: {e}")
        return ""

@app.route('/get_title', methods=['GET'])
def get_title():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # 发送请求获取网页内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 使用 BeautifulSoup 解析标题和内容
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else None
        
        # 尝试获取页面摘要或主要内容
        content = ''
        if soup.find('meta', attrs={'name': 'description'}):
            content = soup.find('meta', attrs={'name': 'description'})['content']
        elif soup.find('p'):
            content = soup.find('p').get_text()[:500]  # 取前500字符

        # 生成标签和关键词
        tags, keywords = generate_tags_and_keywords(title + ' ' + content)
        
        # 生成摘要
        summary = generate_summary(title + ' ' + content)
        
        return jsonify({
            "title": title,
            "url": url,
            "tags": tags,
            "keywords": keywords,
            "summary": summary
        })

    except requests.RequestException as e:
        logging.error("获取网页内容时出错: %s", e)
        return jsonify({
            "error": str(e),
            "url": url
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
