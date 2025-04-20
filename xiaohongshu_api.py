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
    url: str  # Can be either a direct URL or share text with URL
    timeout: Optional[int] = 10
    use_meta_tags: Optional[bool] = True  # Option to use meta tags for extraction

class ShareTextRequest(BaseModel):
    share_text: str  # The text shared from Xiaohongshu app that contains the link
    timeout: Optional[int] = 10
    use_meta_tags: Optional[bool] = True

class ScrapeResponse(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    content: List[str]
    images: List[str]
    success: bool
    message: str
    extracted_link: Optional[str] = None  # For storing the extracted link when using share text

def extract_xiaohongshu_link(share_text: str) -> str:
    """从小红书分享文本中提取链接"""
    # 正则表达式匹配http://xhslink.com/开头的链接
    pattern = r'https?://xhslink\.com/[a-zA-Z0-9/\-_]+'
    match = re.search(pattern, share_text)
    if match:
        return match.group(0)
    
    # 如果没找到，尝试匹配其他可能的小红书链接
    pattern = r'https?://www\.xiaohongshu\.com/\S+'
    match = re.search(pattern, share_text)
    if match:
        return match.group(0)
    
    return None

def is_valid_xiaohongshu_url(url: str) -> bool:
    """验证小红书URL是否有效"""
    try:
        result = urlparse(url)
        # 检查是否是有效的URL
        if not all([result.scheme, result.netloc]):
            return False
        
        # 检查是否是小红书域名 (包括短链域名)
        if not ('xiaohongshu.com' in result.netloc or 'xhslink.com' in result.netloc):
            return False
            
        # 不再严格检查URL路径格式，因为短链接格式不同
        return True
    except:
        return False

def is_valid_url(url: str) -> bool:
    """检查字符串是否是有效的URL"""
    try:
        result = urlparse(url)
        # 检查是否是有效的HTTP/HTTPS URL
        return all([
            result.scheme in ('http', 'https'),
            result.netloc,
        ])
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

def parse_html_content(soup: BeautifulSoup, use_meta_tags: bool = False, base_url: str = None):
    """解析HTML内容并提取信息"""
    title = None
    content = []
    images = []
    
    # 使用meta标签提取内容
    if use_meta_tags:
        # 提取标题 - 从og:title meta标签 (可能使用name或property属性)
        og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
        if og_title and og_title.get('content'):
            title = clean_text(og_title['content'])
        
        # 提取内容 - 从description meta标签
        description = soup.find('meta', property='description') or soup.find('meta', attrs={'name': 'description'})
        if description and description.get('content'):
            content_text = clean_text(description['content'])
            # 将内容按照换行符分割成多个段落
            content = [p.strip() for p in re.split(r'[\n\t]', content_text) if p.strip()]
        
        # 提取图片 - 从og:image meta标签 
        # 直接使用字典方式查找，避免使用property或name属性区分
        for meta in soup.find_all('meta'):
            # 检查是否是og:image标签（可能用name或property属性）
            if (meta.get('property') == 'og:image' or meta.get('name') == 'og:image') and meta.get('content'):
                img_url = meta['content']
                # 只做基本URL验证，小红书图片链接都是http/https开头
                if img_url.startswith(('http://', 'https://')):
                    images.append(img_url)
        
        # 如果上述方法没有找到图片，尝试查找所有可能包含图片的meta标签
        if not images:
            # 打印调试信息
            print("No images found using primary method, trying alternative methods...")
            
            # 列出所有meta标签
            for meta in soup.find_all('meta'):
                # 查找任何可能包含图片的标签
                name = meta.get('name', '')
                prop = meta.get('property', '')
                if ('image' in name.lower() or 'image' in prop.lower()) and meta.get('content'):
                    img_url = meta['content']
                    if img_url.startswith(('http://', 'https://')):
                        images.append(img_url)
                        print(f"Found image: {img_url}")
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
            
            # 确保只返回HTTP/HTTPS URL，过滤掉base64编码的图片
            if img_url and not img_url.startswith('data:'):
                if base_url and not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(base_url, img_url)
                if is_valid_url(img_url):
                    images.append(img_url)
    
    return title, content, images

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_article(request: ScrapeRequest):
    try:
        url = request.url
        extracted_link = None
        
        # 检查是否是分享文本而不是URL
        if not url.startswith(('http://', 'https://')) or len(url) > 100:
            # 尝试提取链接
            extracted_link = extract_xiaohongshu_link(url)
            if extracted_link:
                url = extracted_link
            else:
                raise HTTPException(
                    status_code=400,
                    detail="No valid Xiaohongshu link found in the provided text. Please provide a valid URL or share text containing a URL."
                )
        
        # 验证URL
        if not is_valid_xiaohongshu_url(url):
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
        response = requests.get(url, headers=headers, timeout=request.timeout)
        response.raise_for_status()
        
        # 检查响应状态码
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f'HTTP Error {response.status_code}: {response.reason}'
            )
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析HTML内容
        title, content, images = parse_html_content(soup, request.use_meta_tags, url)
        
        # 如果没有提取到图片，尝试使用正则表达式直接从HTML中提取
        if not images:
            print("尝试使用正则表达式提取图片URL")
            # 匹配og:image meta标签的内容 - 多种可能的格式
            og_image_patterns = [
                r'<meta\s+(?:property|name)="og:image"\s+content="([^"]+)"',  # property/name first
                r'<meta\s+content="([^"]+)"\s+(?:property|name)="og:image"',  # content first
                r'<meta\s+name="og:image"\s+content="([^"]+)"',  # specific to name
                r'<meta\s+content="([^"]+)"\s+name="og:image"',  # content first with name
                r'<meta\s+property="og:image"\s+content="([^"]+)"',  # specific to property
                r'<meta\s+content="([^"]+)"\s+property="og:image"'  # content first with property
            ]
            
            for pattern in og_image_patterns:
                og_image_matches = re.findall(pattern, response.text)
                if og_image_matches:
                    for img_url in og_image_matches:
                        if img_url and img_url.startswith(('http://', 'https://')):
                            if img_url not in images:  # 避免重复添加
                                images.append(img_url)
                                print(f"Using regex pattern '{pattern}' found image: {img_url}")
            
            # 如果具体的模式没有找到，尝试更通用的模式
            if not images:
                # 更通用的模式，可以捕获不同属性顺序和各种空格/引号变化
                general_pattern = r'<meta[^>]*?(?:name|property)\s*=\s*["\'](og:image)["\'][^>]*?content\s*=\s*["\']([^"\']+)["\'][^>]*?>'
                general_matches = re.findall(general_pattern, response.text)
                for _, img_url in general_matches:
                    if img_url and img_url.startswith(('http://', 'https://')):
                        if img_url not in images:
                            images.append(img_url)
                            print(f"Using general regex found image: {img_url}")
                            
                # 反向尝试，content在前，name/property在后
                reverse_pattern = r'<meta[^>]*?content\s*=\s*["\']([^"\']+)["\'][^>]*?(?:name|property)\s*=\s*["\'](og:image)["\'][^>]*?>'
                reverse_matches = re.findall(reverse_pattern, response.text)
                for img_url, _ in reverse_matches:
                    if img_url and img_url.startswith(('http://', 'https://')):
                        if img_url not in images:
                            images.append(img_url)
                            print(f"Using reverse regex found image: {img_url}")
        
        # 检查是否成功获取内容
        if not content and not images:
            return ScrapeResponse(
                title=title,
                subtitle=None,
                content=content,
                images=images,
                success=False,
                message="No content found. The article might be behind a paywall or the URL might be incorrect.",
                extracted_link=extracted_link
            )
        
        return ScrapeResponse(
            title=title,
            subtitle=None,
            content=content,
            images=images,
            success=True,
            message="Content successfully scraped",
            extracted_link=extracted_link
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

@app.post("/scrape-share", response_model=ScrapeResponse)
async def scrape_from_share_text(request: ShareTextRequest):
    try:
        # 从分享文本中提取链接
        url = extract_xiaohongshu_link(request.share_text)
        if not url:
            raise HTTPException(
                status_code=400,
                detail="No valid Xiaohongshu link found in the share text."
            )
        
        # 创建ScrapeRequest对象
        scrape_request = ScrapeRequest(
            url=url,
            timeout=request.timeout,
            use_meta_tags=request.use_meta_tags
        )
        
        # 调用scrape_article函数进行爬取
        result = await scrape_article(scrape_request)
        
        # 添加提取的链接到返回结果
        result.extracted_link = url
        return result
        
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
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
            "/scrape": "POST endpoint for scraping article content from URL",
            "/scrape-share": "POST endpoint for scraping article content from share text",
            "/docs": "API documentation"
        }
    }

@app.post("/debug")
async def debug_html(request: ScrapeRequest):
    """调试端点，用于查看获取到的HTML内容和提取的meta标签"""
    try:
        url = request.url
        extracted_link = None
        
        # 检查是否是分享文本而不是URL
        if not url.startswith(('http://', 'https://')) or len(url) > 100:
            # 尝试提取链接
            extracted_link = extract_xiaohongshu_link(url)
            if extracted_link:
                url = extracted_link
            else:
                raise HTTPException(
                    status_code=400,
                    detail="No valid Xiaohongshu link found in the provided text."
                )
                
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=request.timeout)
        response.raise_for_status()
        
        # 保存原始HTML以供检查
        with open("debug_html.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取所有meta标签
        all_meta_tags = []
        image_meta_tags = []
        
        for meta in soup.find_all('meta'):
            meta_data = {}
            for attr in meta.attrs:
                meta_data[attr] = meta[attr]
            all_meta_tags.append(meta_data)
            
            # 单独收集图片相关的meta标签
            name = meta.get('name', '')
            prop = meta.get('property', '')
            if 'image' in name.lower() or 'image' in prop.lower():
                image_meta_tags.append(meta_data)
                
        # 搜索HTML中所有包含"og:image"的内容
        og_image_patterns = []
        for line in response.text.split('\n'):
            if 'og:image' in line:
                og_image_patterns.append(line.strip())
                
        # 尝试直接提取图片
        title, content, images = parse_html_content(soup, use_meta_tags=True, base_url=url)
            
        return {
            "url": url,
            "extracted_link": extracted_link,
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type'),
            "html_saved": "debug_html.html",
            "all_meta_tags_count": len(all_meta_tags),
            "image_meta_tags": image_meta_tags,
            "og_image_patterns": og_image_patterns,
            "extracted_images": images,
            "html_preview": response.text[:500] + "..." if len(response.text) > 500 else response.text
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Debug error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 