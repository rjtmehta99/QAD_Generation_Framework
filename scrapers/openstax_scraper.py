import constants
import time
import pandas as pd
import selenium_helper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException

def scrape_summaries(subject: str, url: str):
    print(f'Scraping {subject}:')
    browser = selenium_helper.init_browser(url=url)
    chapter_identifier = constants.OPENSTAX_CHAPTER_MAPPING[subject]
    chapters = browser.find_elements(by=By.XPATH, value=f"//li[@data-type='{chapter_identifier}' and @class='styled__NavItem-sc-18yti3s-2 lcPtic']")

    for chapter in chapters:
        try:
            chapter.click()
            time.sleep(2)
        except ElementClickInterceptedException:
            browser.find_element(by=By.XPATH, value="//button[@data-analytics-label='close']").click()
            time.sleep(2)

    subchapters = chapters[0].find_elements(by=By.XPATH, value="//li[@data-type='chapter']")
    # Open all subchapters in dropdowns
    for subchapter in subchapters:
        try:
            subchapter.click()
            browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", subchapter)
            time.sleep(3)
        except ElementClickInterceptedException:
            # Move to fxn
            # Remove overlay popup
            browser.find_element(by=By.XPATH, value="//button[@data-analytics-label='close']").click()
            time.sleep(3)
        except ElementNotInteractableException:
            pass
    
    summary_code = constants.OPENSTAX_SUMMARY_MAPPING[subject]
    summaries = browser.find_elements(by=By.LINK_TEXT, value=summary_code)
    # Save summary URLs
    summary_urls = []
    for summary in summaries:
        url = summary.get_attribute('href')
        summary_urls.append(url)
    
    # Save summary headings and texts
    summary_headings = []
    summary_texts = []
    for url in summary_urls:
        browser.get(url)
        selenium_helper.wait_by_id(browser=browser, value='main-content')
        summary_content = browser.find_element(by=By.ID, value='main-content')
        subsections = summary_content.find_elements(by=By.CLASS_NAME, value='summary')
        for subsection in subsections:
            heading = subsection.find_element(by=By.TAG_NAME, value='a').text
            summary_headings.append(heading)
            
            try:
                text = subsection.find_element(by=By.TAG_NAME, value='p').text
            # Encountered when list (ul) used instead of <p> like for Physics book.
            except NoSuchElementException:
                text = subsection.find_element(by=By.TAG_NAME, value='ul').text
            summary_texts.append(text)
    
    print(f'Saving {subject} to CSV')
    df = pd.DataFrame(data={'summary_heading': summary_headings, 'summary_text': summary_texts, 'subject': subject})
    df.to_csv(f'data/openstax_{subject}.csv', index=False)
    browser.quit()


def run_openstax_scraper(path: str):
    df = pd.read_csv(path)
    df = df.iloc[5:, :]
    for _, row in df.iterrows():
        scrape_summaries(subject=row['subject'], url=row['url'])


if __name__ == '__main__':
    path = 'data/openstax_urls.csv'
    run_openstax_scraper(path)
