from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import zhipuai
from zhipuai import ZhipuAI  # 导入 ZhipuAI 客户端
import os
import logging
import urllib.parse
import hashlib
from PIL import Image, ImageDraw, ImageFont

# 直接在代码中设置环境变量
os.environ['ZHIPUAI_API_KEY'] = 'e8d5a4cd0a1d496de21ed08c64268a85.H8YYYahnU4CRGq8X'
os.environ['APIFLASH_API_KEY'] = '142cb4e790ae4ce1837e072e756061d1'

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

def generate_dynamic_placeholder(hostname, size=128):
    """
    生成动态占位图，包含：
    1. 根据域名生成一致的背景色
    2. 居中显示域名首字母
    3. 高对比度的文字颜色
    """
    # 根据域名生成一致的颜色
    hash_obj = hashlib.md5(hostname.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # 生成柔和的背景色
    r = (hash_int & 0xFF0000) >> 16
    g = (hash_int & 0x00FF00) >> 8
    b = hash_int & 0x0000FF
    
    # 调暗颜色，增加柔和度
    bg_color = (
        min(int(r * 0.7 + 80), 255),
        min(int(g * 0.7 + 80), 255), 
        min(int(b * 0.7 + 80), 255)
    )
    
    # 文字颜色（反色）
    text_color = (255 - bg_color[0], 255 - bg_color[1], 255 - bg_color[2])
    
    # 创建图像
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 选择字体
    try:
        # 尝试使用系统字体
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf"  # Windows
        ]
        font_path = next((path for path in font_paths if os.path.exists(path)), None)
        
        if font_path:
            font = ImageFont.truetype(font_path, size=size//2)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 获取域名首字母（大写）
    first_letter = hostname[0].upper()
    
    # 计算文字位置（居中）
    text_bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size - text_width) / 2, (size - text_height) / 2)
    
    # 绘制文字
    draw.text(position, first_letter, font=font, fill=text_color)
    
    # 保存图像到临时目录
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    output_path = os.path.join(temp_dir, f"{hostname}_placeholder.png")
    
    image.save(output_path)
    
    return output_path

def get_website_thumbnail(url):
    """
    获取网站缩略图
    优先级：
    1. 特定网站官方 Favicon
    2. Google Favicon
    3. 动态生成占位图
    """
    try:
        # 提取主机名，移除 www. 前缀
        hostname = urllib.parse.urlparse(url).hostname.replace('www.', '')
        
        # 特殊域名处理（使用更高质量的图标）
        special_domains = {
            'github.com': 'https://github.githubassets.com/pinned-octocat.svg',
            'stackoverflow.com': 'https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico?v=ec617d715196',
            'gitlab.com': 'https://gitlab.com/assets/favicon-72a2cad5025aa2d1c1d7b6b43c04aaa1.png',
            'bitbucket.org': 'https://bytesized-assets.atlassian.net/assets/img/favicon.png',
            'python.org': 'https://www.python.org/static/favicon.ico',
            'openai.com': 'https://openai.com/favicon.ico'
        }
        
        # 优先使用特殊域名的 Favicon
        if hostname in special_domains:
            logging.info(f"使用特殊域名 Favicon: {special_domains[hostname]}")
            return special_domains[hostname]
        
        # 使用 Google Favicon API，增加图标大小和质量
        favicon_url = f"https://www.google.com/s2/favicons?domain={hostname}&sz=128"
        logging.info(f"尝试使用 Google Favicon: {favicon_url}")
        
        # 验证 Favicon 是否可访问
        try:
            # 允许重定向，获取最终的图标 URL
            response = requests.get(favicon_url, allow_redirects=True, timeout=5)
            
            # 检查响应状态码
            if response.status_code in [200, 301, 302]:
                # 使用最终的 URL
                final_url = response.url
                logging.info(f"成功获取 Google Favicon: {final_url}")
                return final_url
            else:
                logging.warning(f"Google Favicon 请求失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"获取 Google Favicon 时发生错误: {e}")
        
        # 如果 Favicon 获取失败，生成动态占位图
        placeholder_path = generate_dynamic_placeholder(hostname)
        logging.warning(f"使用动态占位图: {placeholder_path}")
        
        # 将本地图片转换为可访问的 URL
        placeholder_url = f"http://localhost:5000/temp/{os.path.basename(placeholder_path)}"
        return placeholder_url
    
    except Exception as e:
        logging.error(f"获取网站缩略图时发生严重错误: {e}")
        placeholder_path = generate_dynamic_placeholder('error')
        return f"http://localhost:5000/temp/{os.path.basename(placeholder_path)}"

@app.route('/get_title', methods=['GET'])
def get_title():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

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
        
        # 获取网站缩略图
        thumbnail = get_website_thumbnail(url)

        return jsonify({
            "title": title,
            "url": url,
            "tags": tags,
            "keywords": keywords,
            "summary": summary,
            "thumbnail": thumbnail
        })

    except requests.RequestException as e:
        logging.error("获取网页内容时出错: %s", e)
        return jsonify({
            "error": str(e),
            "url": url
        }), 500

@app.route('/temp/<filename>')
def serve_temp_file(filename):
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    return send_from_directory(temp_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
