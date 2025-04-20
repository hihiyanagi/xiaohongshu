from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup
import requests
import re
from typing import Optional, List
import json

app = FastAPI(
    title="Xiaohongshu Scraper API",
    description="An API service for scraping Xiaohongshu article content",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    url: HttpUrl
    timeout: Optional[int] = 10

class ScrapeResponse(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    content: List[str]
    images: List[str]
    success: bool
    message: str

def is_valid_url(url: str) -> bool:
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def clean_text(text: str) -> str:
    """清理文本，移除多余的空白字符"""
    if not text:
        return ""
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    return text.strip()

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_article(request: ScrapeRequest):
    try:
        # 验证URL
        if not is_valid_url(str(request.url)):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. Please provide a valid URL starting with http:// or https://"
            )

        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # 发送GET请求获取网页内容
        response = requests.get(str(request.url), headers=headers, timeout=request.timeout)
        response.raise_for_status()
        
        # 检查响应状态码
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f'HTTP Error {response.status_code}: {response.reason}'
            )
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题 - 尝试多种方式
        title = None
        # 方式1：查找post-title类
        title_elem = soup.find(class_='post-title')
        if title_elem:
            title = clean_text(title_elem.get_text())
        
        # 方式2：查找h1标签
        if not title:
            h1_elem = soup.find('h1')
            if h1_elem:
                title = clean_text(h1_elem.get_text())
        
        # 方式3：查找article-title类
        if not title:
            title_elem = soup.find(class_='article-title')
            if title_elem:
                title = clean_text(title_elem.get_text())
        
        # 提取副标题
        subtitle = None
        subtitle_elem = soup.find(class_='subtitle')
        if subtitle_elem:
            subtitle = clean_text(subtitle_elem.get_text())
        
        # 提取正文内容 - 尝试多种方式
        content = []
        
        # 方式1：查找article内容
        article_content = soup.find(class_='body markup')
        if article_content:
            # 获取所有段落
            paragraphs = article_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for p in paragraphs:
                text = clean_text(p.get_text())
                if text:
                    content.append(text)
        
        # 提取图片链接
        images = []
        # 查找所有图片
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                if not img_url.startswith(('http://', 'https://')):
                    img_url = 'https:' + img_url
                images.append(img_url)
        
        # 检查是否成功获取内容
        if not content and not images:
            return ScrapeResponse(
                title=title,
                subtitle=subtitle,
                content=content,
                images=images,
                success=False,
                message="No content found. The article might be behind a paywall or the URL might be incorrect."
            )
        
        return ScrapeResponse(
            title=title,
            subtitle=subtitle,
            content=content,
            images=images,
            success=True,
            message="Content successfully scraped"
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="Request timed out. Please check your internet connection and try again."
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Connection error. Please check your internet connection and try again."
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching the website: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Xiaohongshu Scraper API",
        "endpoints": {
            "/scrape": "POST endpoint for scraping article content",
            "/docs": "API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 