# Xiaohongshu Scraper API

A FastAPI-based service for extracting content from Xiaohongshu articles using either direct URLs or share text.

## Features

- Extract titles, content, and images from Xiaohongshu articles
- Support for extracting links from Xiaohongshu share text
- Smart URL detection: provide either direct URL or share text in the URL field
- Meta tag-based extraction for more reliable content parsing
- Clean and well-structured API responses
- Error handling for various request scenarios

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install fastapi uvicorn requests beautifulsoup4
```

3. Run the API server:

```bash
python xiaohongshu_api.py
```

The server will start at `http://localhost:8000`.

## API Endpoints

### 1. URL-based Scraping

**Endpoint:** `/scrape`

**Method:** POST

**Request Body:** 

You can use this endpoint in two ways:

#### Option 1: Direct URL

```json
{
    "url": "https://www.xiaohongshu.com/explore/XXXXXX",
    "timeout": 10,
    "use_meta_tags": true
}
```

#### Option 2: Share Text (Smart Detection)

```json
{
    "url": "小屁孩陶德发布了一篇小红书笔记，快来看吧！😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息...",
    "timeout": 10,
    "use_meta_tags": true
}
```

The API will automatically detect that this is share text and extract the link from it.

Parameters:
- `url` (required): The Xiaohongshu article URL or share text containing a URL
- `timeout` (optional): Request timeout in seconds (default: 10)
- `use_meta_tags` (optional): Whether to use meta tags for extraction (default: false)

### 2. Share Text-based Scraping

**Endpoint:** `/scrape-share`

**Method:** POST

**Request Body:**

```json
{
    "share_text": "小屁孩陶德发布了一篇小红书笔记，快来看吧！😆 jae0CHZjV76kRRt 😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息...",
    "timeout": 10,
    "use_meta_tags": true
}
```

Parameters:
- `share_text` (required): The text shared from Xiaohongshu app that contains the link
- `timeout` (optional): Request timeout in seconds (default: 10)
- `use_meta_tags` (optional): Whether to use meta tags for extraction (default: true)

### Response Format

Both endpoints return the same response format:

```json
{
    "title": "Article Title",
    "subtitle": null,
    "content": ["Paragraph 1", "Paragraph 2", "..."],
    "images": ["image_url_1", "image_url_2", "..."],
    "success": true,
    "message": "Content successfully scraped",
    "extracted_link": "http://xhslink.com/a/..." // URL extracted from share text (null if direct URL was provided)
}
```

## Example Usage

### Using Python Requests

```python
import requests

# Option 1: URL-based scraping
scrape_data = {
    "url": "https://www.xiaohongshu.com/explore/XXXXXX",
    "use_meta_tags": True
}
response = requests.post("http://localhost:8000/scrape", json=scrape_data)
result = response.json()

# Option 2: Direct share text in URL field (simplest approach)
scrape_data = {
    "url": "小屁孩陶德发布了一篇小红书笔记，快来看吧！😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息...",
    "use_meta_tags": True
}
response = requests.post("http://localhost:8000/scrape", json=scrape_data)
result = response.json()

# Option 3: Share text-based scraping (dedicated endpoint)
share_data = {
    "share_text": "小屁孩陶德发布了一篇小红书笔记，快来看吧！😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息...",
    "use_meta_tags": True
}
response = requests.post("http://localhost:8000/scrape-share", json=share_data)
result = response.json()
```

### Test Scripts

This repository includes test scripts to demonstrate the API:

- `test_smart_scrape.py`: Tests the smart URL detection that handles share text directly in URL field
- `test_share_text.py`: Tests the dedicated share text endpoint
- `test_html_api.py`: Tests direct URL scraping with meta tag extraction

Run the tests:

```bash
python test_smart_scrape.py
```

## Command-line Tool

For quick testing, you can use the included `extract_link.py` command-line tool:

```bash
# Extract link from share text
python extract_link.py "小屁孩陶德发布了一篇小红书笔记，快来看吧！ 😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条"

# Extract link and test by fetching content
python extract_link.py -t "小屁孩陶德发布了一篇小红书笔记，快来看吧！ 😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条"

# Read share text from file
python extract_link.py -f share_text.txt -t
```

## Share Text Link Extraction

The API can extract Xiaohongshu links from share text like this:

```
40 小屁孩陶德发布了一篇小红书笔记，快来看吧！ 😆 jae0CHZjV76kRRt 😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息，打开【小红书】App查看精彩内容！
```

It automatically finds and extracts the `http://xhslink.com/a/JEF7CXDbSuFab` link, and then uses it to scrape the content.

## Example for HTML Meta Tags

Here's an example of the meta tags structure this API can parse:

```html
<meta property="og:title" content="11/8我的爵士三重奏在荻窪velvet sun演出 - 小红书">
<meta name="description" content="open 7:15- start 8:00- 欢迎朋友们来聚！...">
<meta property="og:image" content="http://sns-webpic-qc.xhscdn.com/...">
<meta property="og:image" content="http://sns-webpic-qc.xhscdn.com/...">
```

## License

[MIT](LICENSE)

# YouTube API - Vercel部署指南

这个项目是一个基于Python的YouTube API服务，可以部署到Vercel上作为Serverless Functions运行。

## 功能

通过REST API提供以下功能:

- 搜索YouTube视频
- 获取视频详细信息
- 获取频道信息
- 获取视频评论

## 准备工作

1. **获取YouTube API密钥**

   按照 [youtube_api_guide.md](youtube_api_guide.md) 中的说明获取YouTube Data API v3密钥。

2. **安装Vercel CLI**

   ```bash
   npm install -g vercel
   ```

## 本地开发

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **设置环境变量**

   复制`.env.example`文件并重命名为`.env`，然后添加你的YouTube API密钥：

   ```bash
   cp .env.example .env
   # 编辑.env文件，添加你的API密钥
   ```

3. **本地运行API**

   ```bash
   cd api
   uvicorn index:app --reload
   ```

   现在你可以访问 http://localhost:8000 来使用API。
   
   访问 http://localhost:8000/docs 查看API文档界面。

## 部署到Vercel

1. **登录Vercel**

   ```bash
   vercel login
   ```

2. **部署项目**

   ```bash
   vercel
   ```

   按照提示操作。确保在Vercel设置中添加环境变量`YOUTUBE_API_KEY`。

3. **设置环境变量**

   你可以在Vercel仪表盘中设置环境变量，或者使用CLI:

   ```bash
   vercel env add YOUTUBE_API_KEY
   ```

4. **重新部署（如果需要）**

   ```bash
   vercel --prod
   ```

## API端点

部署后，您可以使用以下端点:

- `GET /` - 欢迎信息和API版本
- `GET /search?query=关键词&max_results=5&language=zh-CN` - 搜索视频
- `GET /videos/{video_id}` - 获取单个视频信息
- `GET /videos?video_ids=id1,id2,id3` - 获取多个视频信息
- `GET /channels/{channel_id}` - 获取频道信息
- `GET /videos/{video_id}/comments?max_results=10` - 获取视频评论

## 注意事项

- Vercel免费计划有一些限制，包括函数执行时间和部署大小
- YouTube API有配额限制，请参考[配额和限制](https://developers.google.com/youtube/v3/getting-started#quota)
- 确保在生产环境中设置适当的CORS策略和API密钥保护

## 使用示例

使用curl获取视频信息:

```bash
curl https://你的vercel域名.vercel.app/videos/VIDEO_ID
```

搜索视频:

```bash
curl https://你的vercel域名.vercel.app/search?query=编程教程&max_results=3
``` 