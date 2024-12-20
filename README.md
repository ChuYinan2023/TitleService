# TitleService 网页标题服务

## 功能描述
TitleService 是一个基于 Flask 的微服务，用于从给定的 URL 提取网页标题、生成标签和关键词。

## 主要特性
- 从网页中提取标题
- 使用 ZhipuAI 智能生成标签和关键词
- 处理网页内容获取的异常情况
- 支持代理配置和网络错误处理

## 依赖环境
- Python 3.8+
- Flask
- requests
- BeautifulSoup4
- zhipuai

## 安装步骤
1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 设置 ZHIPUAI_API_KEY 环境变量

## 运行服务
```bash
python app.py
```

服务将在 `http://localhost:5000` 运行，提供 `/get_title` 接口。

## API 接口
- GET `/get_title?url=<网页地址>`
  返回网页的标题、标签、关键词等信息

返回示例：
```json
{
    "title": "Example Domain",
    "url": "https://example.com",
    "tags": ["技术", "示例"],
    "keywords": ["域名", "网站"],
    "summary": "这是一个示例网页，展示了基本的网站结构。",
    "screenshot": "https://screenshot.apiflash.com/..."
}
```

## 最近更新
- 优化标签和关键词生成逻辑
- 改进网络请求和代理处理
- 增加错误处理机制

## 技术栈
- Flask Web框架
- BeautifulSoup网页解析
- ZhipuAI智能生成
- ApiFlash网站截图
- Requests网络请求库

## 注意事项
- 配置 ZHIPUAI_API_KEY 环境变量
- 建议使用最新版本依赖
- 生产环境控制API调用频率
- 网页内容解析依赖网站结构稳定性
- ApiFlash 有使用配额限制
