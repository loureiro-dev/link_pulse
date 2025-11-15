
# Selenium collector - may require chromedriver and display support
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, re

def setup_driver(user_agent: str = None, headless: bool = True, timeout: int = 25):
    options = Options()
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(timeout)
    return driver

def collect_with_selenium(url: str, driver=None, timeout: int = 25):
    close_driver = False
    if driver is None:
        driver = setup_driver(timeout=timeout)
        close_driver = True
    try:
        driver.get(url)
        time.sleep(2)
        # try clicking elements that might reveal links
        elements = driver.find_elements(By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'whatsapp')]")
        links = set()
        for el in elements[:10]:
            try:
                href = el.get_attribute('href') or el.get_attribute('data-href') or ''
                if href and 'whatsapp' in href.lower():
                    links.add(href)
            except:
                pass
        # parse page source for JS-hidden links
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for script in soup.find_all('script'):
            s = script.string or ''
            matches = re.findall(r'(https?://[^\s\'\"]*whatsapp[^\s\'\"]*)', s, re.IGNORECASE)
            for m in matches:
                links.add(m)
        return list(links)
    finally:
        if close_driver:
            driver.quit()
