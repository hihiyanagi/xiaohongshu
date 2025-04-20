from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup
import requests
import re
from typing import Optional, List
import json
from urllib.parse import urlparse, urljoin
from urllib.error import URLError

app = FastAPI(
    title="Xiaohongshu Scraper API",
    description="An API service for scraping Xiaohongshu article content",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    url: str  # Changed from HttpUrl to str to handle custom URLs
    timeout: Optional[int] = 10
    use_meta_tags: Optional[bool] = False  # Option to use meta tags for extraction

class ScrapeResponse(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    content: List[str]
    images: List[str]
    success: bool
    message: str

def is_valid_xiaohongshu_url(url: str) -> bool:
    """验证小红书URL是否有效"""
    try:
        result = urlparse(url)
        # 检查是否是有效的URL
        if not all([result.scheme, result.netloc]):
            return False
        
        # 检查是否是小红书域名
        if 'xiaohongshu.com' not in result.netloc:
            return False
            
        # 检查URL路径格式
        if not re.match(r'^/explore/\w+', result.path):
            return False
            
        return True
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
        if not is_valid_xiaohongshu_url(request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid Xiaohongshu URL format. Please provide a valid Xiaohongshu article URL."
            )

        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
            'Cookie': 'xhsTrackerId=cebd0f66-36e7-4b2f-99f3-2c047f24b4b2; timestamp2=20210915a50a6e09e6f5d33a4da81d3c; timestamp2.sig=JwvJCkLwzq7qXwKXvLxQdHq1XqQ'  # 添加一些基本的cookie
        }
        
        # 发送GET请求获取网页内容
        response = requests.get(request.url, headers=headers, timeout=request.timeout)
        response.raise_for_status()
        
        # 检查响应状态码
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f'HTTP Error {response.status_code}: {response.reason}'
            )
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = None
        content = []
        images = []
        
        # 使用meta标签提取内容
        if request.use_meta_tags:
            # 提取标题 - 从og:title meta标签
            og_title = soup.find('meta', attrs={'name': 'og:title'}) or soup.find('meta', attrs={'property': 'og:title'})
            if og_title and og_title.get('content'):
                title = clean_text(og_title['content'])
            
            # 提取内容 - 从description meta标签
            description = soup.find('meta', attrs={'name': 'description'})
            if description and description.get('content'):
                content_text = clean_text(description['content'])
                # 将内容按照换行符分割成多个段落
                content = [p.strip() for p in re.split(r'[\n\t]', content_text) if p.strip()]
            
            # 提取图片 - 从og:image meta标签
            for og_image in soup.find_all('meta', attrs={'name': 'og:image'}) or soup.find_all('meta', attrs={'property': 'og:image'}):
                if og_image.get('content'):
                    img_url = og_image['content']
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(request.url, img_url)
                    images.append(img_url)
        else:
            # 传统方式提取内容
            # 提取标题 - 尝试多种方式
            title_elem = soup.find(class_='title')
            if not title_elem:
                title_elem = soup.find(class_='note-title')
            if title_elem:
                title = clean_text(title_elem.get_text())
            
            # 方式2：查找h1标签
            if not title:
                h1_elem = soup.find('h1')
                if h1_elem:
                    title = clean_text(h1_elem.get_text())
            
            # 提取正文内容
            article_content = soup.find(class_='content')
            if not article_content:
                article_content = soup.find(class_='note-content')
                
            if article_content:
                # 获取所有段落
                paragraphs = article_content.find_all(['p', 'div'])
                for p in paragraphs:
                    text = clean_text(p.get_text())
                    if text and len(text.strip()) > 0:
                        content.append(text)
            
            # 提取图片链接
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if not img_url:
                    img_url = img.get('data-src')
                if img_url:
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(request.url, img_url)
                    images.append(img_url)
        
        # 检查是否成功获取内容
        if not content and not images:
            return ScrapeResponse(
                title=title,
                subtitle=None,
                content=content,
                images=images,
                success=False,
                message="No content found. The article might be behind a paywall or the URL might be incorrect."
            )
        
        return ScrapeResponse(
            title=title,
            subtitle=None,
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