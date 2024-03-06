from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import constants
from proprofs_scraper import scrape_proprofs_quiz
import argparse

def scrape_quiz_list(subject: str, base_url: str) -> pd.DataFrame:
    """ Scarapes the titles and URLs of the quizzes from the popular quiz list. """
    page = requests.get(base_url, timeout=10)
    body = BeautifulSoup(page.content, 'html.parser')

    quiz_list_body = body.find('div', {'class': 'descr_area left_wrapper'})
    quiz_list_table = quiz_list_body.find('div', {'class': 'top_image'})
    quiz_list_rows = quiz_list_table.find_all('a', {'style': 'word-break:break-word;'})

    titles = []
    urls = []
    for quiz_row in quiz_list_rows:
        titles.append(quiz_row.text.strip('\n'))
        urls.append(quiz_row['href'])
    
    df = pd.DataFrame(data={'title': titles, 'url': urls})
    df.to_csv(f'data/proprofs_{subject}_index.csv', index=False)
    return df

def main(subject: str, base_url: str) -> None:
    """ Triggers scrapers for a ProProf subject url. """
    df = scrape_quiz_list(subject, base_url)

    for row in df.itertuples():
        full_title = f'{subject} {row.title}'
        full_title = re.sub(' ', '_', full_title)
        scrape_proprofs_quiz(subject=full_title, url=row.url)
    
    print('\n+++++ ProProfs Scraping Completed +++++')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', help='ProProf Subject', required=False, default='Biology')
    parser.add_argument('--base_url', help='ProProf Quiz Base URL', required=False, default=constants.PROPROF_BIO_BASE_URL)
    args = parser.parse_args()
    print(f'\nScraping {args.subject} from {args.base_url}')
    main(args.subject, args.base_url)
