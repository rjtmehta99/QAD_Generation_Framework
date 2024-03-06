import time
import random
import constants
import pandas as pd
import selenium_helper
from selenium.webdriver.common.by import By

def scrape_brightstorm(subject:str, base_url:str) -> pd.DataFrame:
    """
    Scrape any brightstorm url. 
    Scrape URL of individual chapters, their corresponding summaries, and save them to DF.

    Args:
        subject (str): subject name
        base_url (str): base subject URl

    Returns:
        pd.DataFrame: DF with scraped information
    """
    print(f'\nScraping {subject}')
    browser = selenium_helper.browser_headless()
    browser.get(base_url)

    urls = []
    titles = []
    chapter_index = browser.find_element(by=By.ID, value='main')
    chapters = chapter_index.find_elements(by=By.CLASS_NAME, value='unit')
    for chapter in chapters:
        subchatpers = chapter.find_elements(by=By.CLASS_NAME, value='topic-link')
        for subchapter in subchatpers:
            subchatper_link = subchapter.find_element(by=By.TAG_NAME, value='a')
            titles.append(subchatper_link.text)
            subchapter_link = subchatper_link.get_attribute('href')
            urls.append(subchapter_link)

    summaries = []
    for url in urls:
        print(f'Scraping {url}')
        browser.get(url)
        try:
            selenium_helper.wait_by_id(browser=browser, value='explanation')
            time.sleep(random.uniform(2,4))
            summary = browser.find_element(by=By.ID, value='explanation')
            summaries.append(summary.text)
        except Exception as e:
            print(f'Error encountered {e}\nSkipping {url}')
            summaries.append('')
    
    browser.quit()
    df = pd.DataFrame(data={'title': titles, 'summary': summaries, 
                            'subject': subject,'url': urls})
    df.to_csv(f'{constants.BASE_FOLDER}_brightstorm_{subject}.csv', index=False)
    return df


def run_brightstorm_scraper(path):
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        scrape_brightstorm(subject=row['subject'], base_url=row['url'])


if __name__ == '__main__':
    path = 'data/brightstorm_urls.csv'
    run_brightstorm_scraper(path)
