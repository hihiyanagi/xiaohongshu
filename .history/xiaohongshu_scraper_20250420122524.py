import requests
from bs4 import BeautifulSoup
import json
import sys
import argparse

def scrape_xiaohongshu(url):
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
            'Cookie': 'xhsTrackerId=cebd0f66-36e4-4b2f-98f0-2ed8a0ed9e60; timestamp2=20210915f6b0c4b0b0b0b0b0b0b0b0b0b0b0b0; timestamp2.sig=JvXSNpidLNj8rbsNvrlrxQl4Nc-OkpKT29IXiKS9rVGo',
        }
        
        # 发送GET请求获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题 - 尝试多种方式
        title = None
        # 方式1：查找og:title
        og_title = soup.find('meta', attrs={'name': 'og:title'})
        if og_title:
            title = og_title.get('content', '').replace(' - 小红书', '')
        # 方式2：查找title标签
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.replace(' - 小红书', '')
        
        # 提取正文内容 - 尝试多种方式
        content = None
        # 方式1：查找description
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            content = description.get('content', '')
            
        # 方式2：查找正文内容 - 尝试多个可能的class名称
        if not content:
            content_selectors = [
                'div.content',
                'div.body-markup',
                'div.note-content',
                'div.available-content',
                'article.content',
                'div[class*="content"]',  # 包含content的class
                'div[class*="article"]',   # 包含article的class
                'div[class*="text"]'       # 包含text的class
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # 获取所有文本，包括嵌套的元素
                    content = ' '.join([text.strip() for text in content_element.stripped_strings])
                    if content:
                        break
        
        # 方式3：查找所有段落文本
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # 提取图片链接 - 尝试多种方式
        images = []
        # 方式1：查找og:image
        for img in soup.find_all('meta', attrs={'name': 'og:image'}):
            img_url = img.get('content')
            if img_url:
                if not img_url.startswith(('http://', 'https://')):
                    img_url = 'https:' + img_url
                images.append(img_url)
        
        # 方式2：查找img标签
        if not images:
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if img_url:
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = 'https:' + img_url
                    images.append(img_url)
        
        # 提取关键词
        keywords = []
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            keywords = [k.strip() for k in keywords_meta.get('content', '').split(',')]
        
        # 创建结果字典
        result = {
            'title': title,
            'content': content,
            'images': images,
            'keywords': keywords
        }
        
        # 打印HTML内容以便调试
        # print("HTML Content:")
        # print(soup.prettify())
        
        return result
        
    except requests.RequestException as e:
        return {'error': f'Error fetching the website: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Scrape content from Xiaohongshu')
    parser.add_argument('url', help='The URL of the Xiaohongshu page to scrape')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--debug', '-d', action='store_true', help='Print debug information')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查URL是否有效
    if not args.url.startswith('https://www.xiaohongshu.com/'):
        print('Error: URL must be from xiaohongshu.com')
        sys.exit(1)
    
    # 抓取内容
    result = scrape_xiaohongshu(args.url)
    
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