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
        # 方式2：查找正文内容
        if not content:
            content_div = soup.find('div', class_='content')
            if content_div:
                content = content_div.get_text(strip=True)
        
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
    url = 'https://www.xiaohongshu.com/explore/672623ad000000001d03a670?source=webshare&xhsshare=pc_web&xsec_token=AB6zBBbrTaHjVj8PHb-ukm3hZOkdLKgWlHrJf0lvwS-i4=&xsec_source=pc_share'
    
    # 抓取内容
    result = scrape_xiaohongshu(url)
    
    # 打印结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 