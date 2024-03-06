import requests
import constants
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_proprofs_quiz(subject: str, url: str) -> None:
    """
    Scrapes questions, answers and correct choices for a give
    """
    page = requests.get(url, timeout=10)
    body = BeautifulSoup(page.content, 'html.parser')
    table = body.find('ul', {'class': 'questions-list'})
    rows = table.find_all('li', {'class': 'ques_marg'})

    questions = []
    choices = []
    correct_choices = []

    for row in rows:
        question = row.find('h3', {'class': 'question-text'}).text
        questions.append(question)
        choice_rows = row.find_all('li', {'class': 'list_multichoice'})
        choice_texts = [re.sub('\n', '', choice.text) for choice in choice_rows]
        choices.append(choice_texts)
        correct_choice = row.find('div', {'class': 'correct_ans_list'}).text
        correct_choice = re.sub('Correct Answer', '', correct_choice)
        correct_choices.append(correct_choice)

    df = pd.DataFrame(data={'question': questions, 'choices': choices, 'correct_choices': correct_choices})
    df.to_csv(f'data/proprofs_{subject}.csv', index=False)