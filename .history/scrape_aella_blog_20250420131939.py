import requests
from bs4 import BeautifulSoup
import time
import re
import random

def clean_text(text):
    """清理和格式化文本"""
    # 删除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 删除空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def get_text_from_element(element):
    """递归获取元素中的所有文本内容"""
    if element.name in ['script', 'style', 'noscript']:
        return ''
    
    # 如果是换行标签，直接返回换行符
    if element.name == 'br':
        return '\n'
    
    # 获取当前元素的直接文本内容
    text = ''
    for child in element.children:
        if isinstance(child, str):
            text += child
        else:
            text += get_text_from_element(child)
    
    # 根据标签类型添加适当的格式
    if element.name in ['p', 'div']:
        text = text.strip() + '\n\n'
    elif element.name in ['span', 'em']:
        text = text.strip() + ' '
    
    return text

def scrape_aella_blog():
    # URL of the blog post
    url = "https://aella.substack.com/p/which-kinksters-are-the-most-mentally"
    
    # Add comprehensive headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
    }
    
    try:
        # Add a random delay between 1-3 seconds
        time.sleep(random.uniform(1, 3))
        
        # Send GET request to the URL
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', class_='available-content')
        
        if content_div:
            # 获取所有文本内容
            content = ''
            
            # 首先尝试获取文章主体
            article = content_div.find('article')
            if article:
                content_div = article
            
            # 遍历所有可能包含内容的元素
            for element in content_div.find_all(['p', 'div', 'span', 'em', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                if element.parent.name not in ['p', 'div', 'span', 'em']:  # 避免重复内容
                    text = get_text_from_element(element)
                    if text:
                        content += text
            
            # 如果内容为空，尝试其他方法
            if not content.strip():
                # 尝试获取所有文本节点
                content = content_div.get_text(separator='\n', strip=True)
            
            # 清理和格式化文本
            content = clean_text(content)
            
            # 检查是否获取到了有效内容
            if len(content.strip()) < 100:  # 如果内容太短，可能是被付费墙阻止
                print("Warning: Very little content was retrieved. The content might be behind a paywall.")
            
            # 写入文件
            with open('blog_content.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Content has been successfully scraped and saved to 'blog_content.txt'")
            print(f"Content length: {len(content)} characters")
        else:
            print("Could not find the main content div")
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the webpage: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    scrape_aella_blog() 