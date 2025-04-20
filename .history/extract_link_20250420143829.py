#!/usr/bin/env python3
import re
import sys
import argparse
import requests
from bs4 import BeautifulSoup

def extract_xiaohongshu_link(share_text):
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

def get_meta_content(html_text):
    """从HTML内容中提取元标签信息"""
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # 提取标题
    title = None
    og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
    if og_title and og_title.get('content'):
        title = og_title['content'].strip()
    
    # 提取描述
    description = None
    desc_tag = soup.find('meta', property='description') or soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        description = desc_tag['content'].strip()
    
    # 提取图片URL
    images = []
    for og_image in soup.find_all('meta', property='og:image') or soup.find_all('meta', attrs={'name': 'og:image'}):
        if og_image.get('content'):
            images.append(og_image['content'])
    
    return {
        'title': title,
        'description': description,
        'images': images
    }

def main():
    parser = argparse.ArgumentParser(description='Extract and test Xiaohongshu links from share text')
    parser.add_argument('share_text', nargs='?', help='The share text containing a Xiaohongshu link')
    parser.add_argument('-f', '--file', help='Read share text from a file')
    parser.add_argument('-t', '--test', action='store_true', help='Test the extracted link by fetching content')
    
    args = parser.parse_args()
    
    # 获取分享文本
    share_text = ""
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                share_text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    elif args.share_text:
        share_text = args.share_text
    else:
        print("Please provide share text either directly or via a file.")
        return 1
    
    # 提取链接
    link = extract_xiaohongshu_link(share_text)
    if not link:
        print("No Xiaohongshu link found in the provided text.")
        return 1
    
    print(f"Extracted Link: {link}")
    
    # 测试链接
    if args.test:
        try:
            print("\nFetching content from the link...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Referer': 'https://www.xiaohongshu.com/'
            }
            
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            
            meta_content = get_meta_content(response.text)
            
            print("\n===== Content Information =====")
            print(f"Title: {meta_content['title'] or 'Not found'}")
            
            if meta_content['description']:
                desc = meta_content['description']
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"Description: {desc}")
            else:
                print("Description: Not found")
            
            print(f"Number of images: {len(meta_content['images'])}")
            if meta_content['images']:
                for i, img in enumerate(meta_content['images'][:3], 1):
                    print(f"Image {i}: {img}")
                if len(meta_content['images']) > 3:
                    print(f"... and {len(meta_content['images']) - 3} more images")
            
        except Exception as e:
            print(f"Error fetching content: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 