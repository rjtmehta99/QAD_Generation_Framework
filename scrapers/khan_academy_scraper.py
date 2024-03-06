# Work in Progress 
from __future__ import annotations
import re
import random
import constants
import pandas as pd
import selenium_helper
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException


def move_to_next_ques(browser: WebDriver, answer_btns: list[FirefoxWebElement]) -> WebDriver:
    for answer_btn in answer_btns:        
        answer_btn.click()
        selenium_helper.default_sleep()
        browser = selenium_helper.click_by_xpath(browser, constants.CHECK_ANSWER_BTN_XPATH)

        try:
            # Check if alert generated
            incorrect_answer_popover = browser.find_element(by=By.XPATH, value=constants.MULTIPLE_POPOVERS)
            selenium_helper.default_sleep()
            print('Incorrect answer clicked')

            # Incorrect answer
            try:
                browser = selenium_helper.click_btn_by_text(browser=browser, text='skip for now')
                break
            except NoSuchElementException:
                browser = selenium_helper.click_btn_by_text(browser=browser, text='move on')
                break
        
        # Triggered if no alert generated
        except NoSuchElementException:
            browser = selenium_helper.click_by_xpath(browser, constants.NEXT_QUESTION_BTN)
            break
    return browser


def begin_quiz(browser: WebDriver) -> WebDriver:
    # Begin Quiz
    try:
        selenium_helper.default_sleep()
        donation_banner = browser.find_element(by=By.ID, value='donate-banner')
        donation_banner.find_element(by=By.XPATH, value=constants.CLOSE_DONATION_BANNER).click()
        #selenium_helper.click_by_id(browser=browser, id_=constants.CLOSE_DONATION_BANNER)
    except NoSuchElementException:
        pass
    selenium_helper.wait_by_class(browser=browser, value=constants.BEGIN_TEST_CLASS)
    begin_btn = browser.find_element(by=By.CLASS_NAME, value=constants.BEGIN_TEST_CLASS)
    actions = ActionChains(browser)
    actions.move_to_element(begin_btn).click().perform()
    return browser


def scrape_khan_academy(subject: str, url: str):
    browser = selenium_helper.init_browser(url)
    browser = begin_quiz(browser)

    scraped_questions = []
    scraped_possible_answers = []
    scraped_correct_answers = []

    for question_index in range(30):
        question = ''
        possible_answers = []

        # Process QA
        question_type = browser.find_elements(by=By.CLASS_NAME, value=constants.QUESTION_TYPE)
        single_answer_question = [True for val in question_type if 'Choose 1 answer:'==val.text]
        # Find answer
        answer_btns = browser.find_elements(by=By.XPATH, value=constants.ANSWER_ROW)

        usable_ques_flag = False
        if any(single_answer_question):
            # Scrape multi-line question
            question_texts = browser.find_elements(by=By.XPATH, value=constants.MULTILINE_QUESTION_TEXT)
            for ques in question_texts:
                if ('Choose' and 'answer') in ques.text:
                    break
                else:
                    print(ques.text)
                    question += ques.text
                    usable_ques_flag = True
        else:
            browser = move_to_next_ques(browser=browser, answer_btns=answer_btns)
            continue

        # Move on to next question if not usable question
        if not usable_ques_flag:
            browser = move_to_next_ques(browser=browser, answer_btns=answer_btns)
        # For a usable question, apply brute force to find answer
        else:
            # Get all answer texts
            for answer in answer_btns:
                try:
                    answer_text = answer.text.split('\n')[1]
                    print(answer_text)
                    possible_answers.append(answer_text)
                except IndexError:
                    break
                
            # Select answer
            for answer_index, answer_btn in enumerate(answer_btns):
                #attribute_name = answer_btn.get_attribute('class')
                selected_class = 'perseus-radio-selected'
                #browser.execute_script(f"arguments[0].classList.add('{selected_class}')", answer_btn)
                answer_btn.click()
                selenium_helper.default_sleep()

                # Click on check
                check_answer_btn = browser.find_element(by=By.XPATH, value=constants.CHECK_ANSWER_BTN_XPATH)            
                # Multiple clicks on submit only for first submission
                if question_index==0 and answer_index==0:
                    check_answer_btn.click()
                    selenium_helper.default_sleep()
                    check_answer_btn.click()
                    selenium_helper.default_sleep()
                check_answer_btn.click()
                selenium_helper.default_sleep(3.0)
                
                try:
                    incorrect_answer_alert = browser.find_element(by=By.XPATH, value=constants.INCORRECT_POPOVER)
                    selenium_helper.default_sleep()
                except NoSuchElementException:
                    correct_answer_selected = len(browser.find_elements(by=By.XPATH, value=constants.CORRECT_POPOVER)) > 0
                    if correct_answer_selected:
                        break
                    else:
                        continue

            # Find correct answer
            checked_answers = browser.find_elements(by=By.XPATH, value=constants.ANSWER_ROW)

            # Dict containing answer index (A, B etc) and answer status (CORRECT / INCORRECT)
            answer_status = {}
            options_list = ['A', 'B', 'C', 'D', 'E', 'F']
            for index, answer in enumerate(checked_answers):
                lines = answer.text.split('\n')
                status = lines[0]
                if '(SELECTED)' in status:
                    status = re.sub(r' \(SELECTED\)', '', status)
                answer_status[options_list[index]] = status
            '''
            try:
                correct_answer = [key for key, value in answer_status.items() if value=='CORRECT'][0]
            except IndexError:
                print('Skipping to next question')
                try:
                    browser.find_element_by_link_text('skip for now')
                except:
                    browser.find_element_by_link_text('move on')
                continue
            '''
            correct_answer = [key for key, value in answer_status.items() if value=='CORRECT'][0]
            scraped_questions.append(question)
            scraped_possible_answers.append(possible_answers)
            scraped_correct_answers.append(correct_answer)

            # Move to next question        
            browser = selenium_helper.click_by_xpath(browser, constants.NEXT_QUESTION_BTN)
            random_sleep_duration = random.uniform(constants.SLEEP_LOWER_LIMIT, constants.SLEEP_HIGHER_LIMIT)
            selenium_helper.default_sleep(random_sleep_duration)

    browser.quit()
    df = pd.DataFrame(data={'questions':scraped_questions, 
                            'possible_answer':scraped_possible_answers, 
                            'correct_answer':scraped_correct_answers})
    df.to_csv(f'data/khanacademy_{subject}_v2.csv', index=False)

if __name__ == '__main__':
    for subject, url in constants.KHANACADEMY_BIOLOGY_MAPPING.items():
        scrape_khan_academy(subject, url)
    