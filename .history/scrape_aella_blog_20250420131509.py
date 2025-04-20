import requests
from bs4 import BeautifulSoup
import time

def scrape_aella_blog():
    # URL of the blog post
    url = "https://aella.substack.com/p/which-kinksters-are-the-most-mentally"
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content div (based on the HTML structure shown in the screenshot)
        content_div = soup.find('div', class_='available-content')
        
        if content_div:
            # Extract all paragraphs
            paragraphs = content_div.find_all('p')
            
            # Create a text file to save the content
            with open('blog_content.txt', 'w', encoding='utf-8') as f:
                for p in paragraphs:
                    # Get the text content and write to file
                    text = p.get_text().strip()
                    if text:  # Only write non-empty paragraphs
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