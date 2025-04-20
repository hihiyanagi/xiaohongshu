from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import uvicorn
from typing import Optional

app = FastAPI(
    title="Web Scraper API",
    description="A FastAPI service for scraping web content using Selenium",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    url: str
    wait_time: Optional[int] = 5
    timeout: Optional[int] = 30

class ScrapeResponse(BaseModel):
    title: str
    subtitle: str
    content: str
    content_length: int
    status: str

def clean_text(text):
    """清理和格式化文本"""
    if not text:
        return ""
    # 删除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 删除空行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def init_driver():
    """初始化WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_content(request: ScrapeRequest):
    driver = None
    try:
        # 初始化WebDriver
        driver = init_driver()
        driver.set_page_load_timeout(request.timeout)
        
        # 访问目标URL
        driver.get(request.url)
        
        # 等待页面加载完成
        time.sleep(request.wait_time)
        
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
            return ScrapeResponse(
                title=title,
                subtitle=subtitle,
                content=full_content,
                content_length=len(full_content),
                status="warning: content might be behind a paywall"
            )
        
        return ScrapeResponse(
            title=title,
            subtitle=subtitle,
            content=full_content,
            content_length=len(full_content),
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if driver:
            driver.quit()

@app.get("/")
async def root():
    return {"message": "Welcome to the Web Scraper API. Use POST /scrape to scrape content."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 