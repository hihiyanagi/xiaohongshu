import requests
from bs4 import BeautifulSoup
import json
import sys
import argparse
import re

def clean_text(text):
    """清理文本，移除多余的空白字符"""
    if not text:
        return ""
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    return text.strip()

def scrape_article(url):
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # 发送GET请求获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
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
        
        # 创建结果字典
        result = {
            'title': title,
            'subtitle': subtitle,
            'content': content,
            'images': images
        }
        
        return result
        
    except requests.RequestException as e:
        return {'error': f'Error fetching the website: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Scrape content from web articles')
    parser.add_argument('url', help='The URL of the article to scrape')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--debug', '-d', action='store_true', help='Print debug information')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 抓取内容
    result = scrape_article(args.url)
    
    # 格式化输出
    output = json.dumps(result, indent=2, ensure_ascii=False)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Results saved to {args.output}')
    else:
        print(output)

if __name__ == '__main__':
    main() 