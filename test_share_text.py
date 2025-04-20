import requests
import json

def test_share_text_api():
    """Test the Xiaohongshu API with share text input"""
    
    # Sample share text as provided in the example
    share_text = "40 小屁孩陶德发布了一篇小红书笔记，快来看吧！ 😆 jae0CHZjV76kRRt 😆 http://xhslink.com/a/JEF7CXDbSuFab，复制本条信息，打开【小红书】App查看精彩内容！"
    
    # API endpoint (assuming the FastAPI app is running locally)
    api_url = "http://localhost:8000/scrape-share"
    
    # Prepare the request payload
    payload = {
        "share_text": share_text,
        "use_meta_tags": True
    }
    
    # Send the request to the API
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        
        # Print the results
        print("\n===== API RESPONSE =====")
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Extracted Link: {data['extracted_link']}")
        
        print("\n===== CONTENT =====")
        print(f"Title: {data['title']}")
        
        print("\nContent paragraphs:")
        for i, paragraph in enumerate(data['content'], 1):
            print(f"{i}. {paragraph}")
        
        print("\nImages:")
        for i, image in enumerate(data['images'], 1):
            print(f"{i}. {image}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_share_text_api() 