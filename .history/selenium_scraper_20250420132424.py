from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def clean_text(text):
    """清理和格式化文本"""
    if not text:
        return ""
    # 删除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 删除空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def scrape_with_selenium():
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 添加用户代理
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        # 初始化WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        
        # 访问目标URL
        url = "https://aella.substack.com/p/which-kinksters-are-the-most-mentally"
        driver.get(url)
        
        # 等待页面加载完成
        time.sleep(5)  # 给页面一些时间加载
        
        # 等待entry div出现
        wait = WebDriverWait(driver, 10)
        entry_div = wait.until(EC.presence_of_element_located((By.ID, "entry")))
        
        # 获取标题
        title = ""
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.post-title")
            title = clean_text(title_elem.text)
        except:
            print("Could not find title")
        
        # 获取副标题
        subtitle = ""
        try:
            subtitle_elem = driver.find_element(By.CSS_SELECTOR, "h3.subtitle")
            subtitle = clean_text(subtitle_elem.text)
        except:
            print("Could not find subtitle")
        
        # 获取主要内容
        content = []
        try:
            # 获取所有段落
            paragraphs = entry_div.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = clean_text(p.text)
                if text:
                    content.append(text)
            
            # 获取所有标题
            headers = entry_div.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            for h in headers:
                text = clean_text(h.text)
                if text:
                    content.append(text)
        except Exception as e:
            print(f"Error extracting content: {e}")
        
        # 组合所有内容
        full_content = f"{title}\n\n{subtitle}\n\n" + "\n\n".join(content)
        
        # 清理最终内容
        full_content = clean_text(full_content)
        
        # 检查内容长度
        if len(full_content.strip()) < 100:
            print("Warning: Very little content was retrieved. The content might be behind a paywall.")
        
        # 保存内容到文件
        with open('blog_content_selenium.txt', 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"Content has been successfully scraped and saved to 'blog_content_selenium.txt'")
        print(f"Content length: {len(full_content)} characters")
        
        # 保存页面截图用于调试
        driver.save_screenshot('page_screenshot.png')
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    scrape_with_selenium() 