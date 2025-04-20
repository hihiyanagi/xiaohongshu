import requests
from bs4 import BeautifulSoup
import json

def scrape_website(url):
    try:
        # 发送GET请求获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.title.string if soup.title else "No title found"
        
        # 提取正文内容
        # 这里我们尝试获取所有段落文本
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        content = ' '.join(paragraphs) if paragraphs else "No content found"
        
        # 提取图片链接
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                # 处理相对URL
                if img_url.startswith('/'):
                    img_url = url + img_url
                elif not img_url.startswith(('http://', 'https://')):
                    img_url = url + '/' + img_url
                images.append(img_url)
        
        # 创建结果字典
        result = {
            'title': title,
            'content': content,
            'images': images
        }
        
        return result
        
    except requests.RequestException as e:
        return {'error': f'Error fetching the website: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

def main():
    # 目标网站URL
    url = 'https://winonawee.com/'
    
    # 抓取内容
    result = scrape_website(url)
    
    # 打印结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 