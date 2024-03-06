import time
import constants
import pandas as pd
#from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium_helper
import ck12_content
from selenium.webdriver import ActionChains

def scrape_chapter_index(subject: str, base_url: str):
    print(f'Scraping {subject}')
    titles = []
    urls = []
    
    browser = selenium_helper.init_browser(url=base_url)
    selenium_helper.wait_by_id(browser, constants.CHAPTER_TABLE)
    chapter_table = browser.find_element(by=By.ID, value=constants.CHAPTER_TABLE)
    chapter_rows = chapter_table.find_elements(by=By.XPATH, value=constants.CHAPTER_ROWS)
    
    # Open all dropdowns
    print(f'Opening all dropdowns')
    for row in chapter_rows:
        #browser.execute_script("arguments[0].setAttribute('data-state', 'open');", row)
        browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", row)
        time.sleep(3)
        #element = driver.find_element_by_tag_name("body")
        #height = str(browser.execute_script("return document.documentElement.scrollHeight") + 25)
        #browser.execute_script(f"window.scrollTo(0, {height})")        
        #time.sleep(3)
        #browser.execute_script("window.scrollTo(0, 100)")
        #time.sleep(3)
        row.click()
        
    # Read subchapter title and URLs
    print(f'Saving all titles and urls to CSV.')
    subchapters = chapter_rows[0].find_elements(by=By.XPATH, value=constants.SUBCHAPTER_URL)
    for subchapter in subchapters:
        titles.append(subchapter.text)
        url = subchapter.get_attribute('href')
        urls.append(url)

    df_index = pd.DataFrame(data={'title':titles, 'url':urls, 'subject':subject})
    df_index.to_csv(f'data/{subject}_index.csv', index=False)
    browser.quit()
    return df_index

def run_ck12_scraper(path: str):
    df_urls = pd.read_csv(path)
    #df_urls = df_urls.iloc[3:4,:]
    for _, row in df_urls.iterrows():
        df = scrape_chapter_index(subject=row['subject'], base_url=row['url'])
        ck12_content.scrape_content(subject=row['subject'], df=df)
    
if __name__ == '__main__':
    path = 'data/ck12_urls.csv'
    run_ck12_scraper(path)
    