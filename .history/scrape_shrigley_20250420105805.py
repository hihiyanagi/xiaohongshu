import requests
from bs4 import BeautifulSoup
import json

def scrape_shrigley_website(url):
    """
    Scrapes the David Shrigley website and extracts title, text, icons, and image links.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        dict: A dictionary containing the scraped information
    """
    try:
        # Send a GET request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract text content (looking for main content areas)
        text_content = []
        for p in soup.find_all('p'):
            if p.text.strip():
                text_content.append(p.text.strip())
        
        # Extract icons (social media links)
        icons = []
        for link in soup.find_all('a', href=True):
            if any(social in link['href'].lower() for social in ['instagram', 'facebook', 'twitter', 'youtube']):
                icons.append({
                    'platform': link['href'].split('.')[1],
                    'url': link['href']
                })
        
        # Extract image links
        image_links = []
        for img in soup.find_all('img'):
            if img.get('src'):
                image_links.append(img['src'])
        
        # Create the result dictionary
        result = {
            'title': title,
            'text_content': text_content,
            'icons': icons,
            'image_links': image_links
        }
        
        return result
        
    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # The URL to scrape
    url = "https://davidshrigley.com/"
    
    # Scrape the website
    result = scrape_shrigley_website(url)
    
    if result:
        # Print the results in a formatted way
        print("\n=== Scraping Results ===\n")
        print(f"Title: {result['title']}\n")
        
        print("Text Content:")
        for i, text in enumerate(result['text_content'], 1):
            print(f"{i}. {text}")
        
        print("\nIcons:")
        for icon in result['icons']:
            print(f"- {icon['platform']}: {icon['url']}")
        
        print("\nImage Links:")
        for i, img_link in enumerate(result['image_links'], 1):
            print(f"{i}. {img_link}")
        
        # Save results to a JSON file
        with open('shrigley_scrape_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("\nResults have been saved to 'shrigley_scrape_results.json'")

if __name__ == "__main__":
    main() 