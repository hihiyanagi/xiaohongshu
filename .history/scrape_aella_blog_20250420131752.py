import requests
from bs4 import BeautifulSoup
import time

def get_text_from_element(element):
    """递归获取元素中的所有文本内容"""
    if element.name in ['script', 'style']:
        return ''
    
    text = ''
    for child in element.children:
        if isinstance(child, str):
            text += child.strip() + ' '
        elif child.name == 'br':
            text += '\n'
        else:
            text += get_text_from_element(child)
    return text.strip()

def scrape_aella_blog():
    # URL of the blog post
    url = "https://aella.substack.com/p/which-kinksters-are-the-most-mentally"
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', class_='available-content')
        
        if content_div:
            # Create a text file to save the content
            with open('blog_content.txt', 'w', encoding='utf-8') as f:
                # 遍历所有内容块
                for element in content_div.find_all(['p', 'div', 'span', 'em']):
                    # 获取元素的文本内容
                    text = get_text_from_element(element)
                    
                    # 如果文本不为空，写入文件
                    if text:
                        f.write(text + '\n\n')
            
            print("Content has been successfully scraped and saved to 'blog_content.txt'")
        else:
            print("Could not find the main content div")
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the webpage: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    scrape_aella_blog() 