import requests
from bs4 import BeautifulSoup
import re

def scrape_article(url):
    """
    Scrape article content from a given URL.
    Returns title, content, and image links.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title = soup.find('h1').text.strip() if soup.find('h1') else "Title not found"
        
        # Extract the main content
        # Look for the main article content
        content_div = soup.find('div', class_=re.compile('post-content'))
        if content_div:
            content = content_div.get_text(separator='\n', strip=True)
        else:
            content = "Content not found"
        
        # Extract image links
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(src)
        
        return {
            'title': title,
            'content': content,
            'images': images
        }
    
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # Example usage
    url = "https://aella.substack.com/p/which-kinksters-are-the-most-mentally"
    result = scrape_article(url)
    
    if result:
        print("\nTitle:")
        print(result['title'])
        
        print("\nContent:")
        print(result['content'])
        
        print("\nImages:")
        for img in result['images']:
            print(img)

if __name__ == "__main__":
    main() 