# 书签管理器标题获取微服务

## 最近更新
### 智能信息提取功能
- 引入基于智谱AI的智能摘要生成
- 自动提取网页标签和关键词
- 优化网页信息解析算法
- 增强错误处理和日志记录机制

## 依赖安装
```bash
pip install -r requirements.txt
```

## 运行服务
```bash
python app.py
```

服务将在 `http://localhost:5000` 运行，提供 `/get_title` 接口。

## 接口使用
GET `/get_title?url=https://example.com`

返回示例：
```json
{
    "title": "Example Domain",
    "url": "https://example.com",
    "tags": ["技术", "示例"],
    "keywords": ["域名", "网站"],
    "summary": "这是一个示例网页，展示了基本的网站结构。"
}
```

## 功能详情

### 智能摘要生成
- 使用AI技术从网页内容中提取核心信息
- 支持自定义摘要长度（默认300字符）
- 处理各种网页内容的边界情况
- 保证摘要简洁、准确

### 自动标签和关键词提取
- 智能分析网页内容
- 最多生成5个相关标签
- 最多生成5个核心关键词
- 支持不同类型网站的个性化提取

### 网页信息解析
- 多源信息提取（meta description, 首段内容）
- 智能处理各种网页结构
- 兼容性强，适应不同网站

## 技术栈
- Flask Web框架
- BeautifulSoup网页解析
- ZhipuAI智能生成
- Requests网络请求库

## 注意事项
- 配置 ZHIPUAI_API_KEY 环境变量
- 建议使用最新版本依赖
- 生产环境控制API调用频率
- 网页内容解析依赖网站结构稳定性
