import requests
from bs4 import BeautifulSoup
import json

def scrape_xiaohongshu(url):
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
        
        # 提取标题
        title = None
        og_title = soup.find('meta', attrs={'name': 'og:title'})
        if og_title:
            title = og_title.get('content', '').replace(' - 小红书', '')
        
        # 提取正文内容
        content = None
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            content = description.get('content', '')
        
        # 提取图片链接
        images = []
        # 查找所有og:image标签
        for img in soup.find_all('meta', attrs={'name': 'og:image'}):
            img_url = img.get('content')
            if img_url:
                images.append(img_url)
        
        # 提取关键词
        keywords = []
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            keywords = keywords_meta.get('content', '').split(',')
        
        # 创建结果字典
        result = {
            'title': title,
            'content': content,
            'images': images,
            'keywords': keywords
        }
        
        return result
        
    except requests.RequestException as e:
        return {'error': f'Error fetching the website: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

def main():
    # 目标网站URL
    url = 'https://www.xiaohongshu.com/explore/672623ad000000001d03a670'
    
    # 抓取内容
    result = scrape_xiaohongshu(url)
    
    # 打印结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 