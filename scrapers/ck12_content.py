import re
import time
import constants
import random
import selenium_helper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pandas import DataFrame

def scrape_content(subject: str, df:DataFrame):
    scraped_texts = []
    browser = selenium_helper.browser_headless()

    for _, row in df.iterrows():
        time.sleep(random.uniform(7,10))
        print(f'Scraping {row["title"]}')
        browser.get(row['url'])
        selenium_helper.wait_by_class(browser, value=constants.CHAPTER_CONTENT)
        try:
            content = browser.find_element(by=By.CLASS_NAME, value=constants.CHAPTER_CONTENT)
            text = content.text
        except NoSuchElementException:
            content = browser.find_element(by=By.ID, value=constants.FALLBACK_CHAPTER_CONTENT)
            text = content.text
        except:
            print(f'\n\n######### COULD NOT LOAD CONTENT FOR {subject} #########\n')
            text = ''
            
        # Remove content after Explore More
        stage_0 = re.sub('Review.*', ' ', text, flags=re.DOTALL)
        stage_1 = re.sub(r'@\$(.*?)@\$',' ', stage_0)
        # Remove [Figure [0-9]+]
        stage_2 = re.sub(r'\[Figure \d+\]', ' ', stage_1)
        blacklist_words = ['figure shows', 'image shows', 'figure describes', 'is shown', 'figure']
        sentences = stage_2.split('.')
        '''
        # Equivalent list compr below
        for sent in sentences:
            if not any(word in sent for word in blacklist_words):
                filtered_sentences.append(sent)
        '''
        sentences_filtered = [sent for sent in sentences if not any(word in sent for word in blacklist_words)]
        text_filter = '.'.join(sentences_filtered)
        scraped_texts.append(text_filter)
    
    df['content'] = scraped_texts
    filename = f'data/{subject}_content.csv'
    print(f'Saving scraped content to {filename}.')
    df.to_csv(filename, index=False)
    browser.quit()
    #return df

