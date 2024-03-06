import time
import constants
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


def init_browser(url: str) -> WebDriver:
    print(f'Opening browser for {url} in headfull.')
    browser = webdriver.Firefox()
    browser.get(url)
    browser.maximize_window()
    return browser


def browser_headless(maximize: bool=False) -> WebDriver:
    """
    Open Firefox in headless mode.
    
    Args:
        maximize (boolean): Optional arg to maximize window.
    """
    print(f'Initiating browser in headless mode.')
    options = webdriver.FirefoxOptions()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    if maximize:
        browser.maximize_window()
    return browser


def wait_by_class(browser: WebDriver, value: str) -> None:
    """
    Wait for element to be loaded.

    Element to be found using class attribute.
    """
    try:
        WebDriverWait(browser, constants.ELEMENT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, value)))
    except:
        print('[ERROR] Element not loaded error')


def wait_by_id(browser: WebDriver, value: str) -> None:
    """
    Wait for element to be loaded.

    Element to be found using id attribute.
    """
    try:
        WebDriverWait(browser, constants.ELEMENT_TIMEOUT).until(EC.presence_of_element_located((By.ID, value)))
    except:
        print('[ERROR] Element not loaded error')


def default_sleep(duration: float=2.0):
    time.sleep(duration)


def click_btn_by_text(browser: WebDriver, text: str) -> WebDriver:
    btn = browser.find_element(by=By.LINK_TEXT, value=text)
    btn.click()
    default_sleep()
    return browser


def click_by_xpath(browser: WebDriver, xpath: str) -> WebDriver:
    btn = browser.find_element(by=By.XPATH, value=xpath)
    btn.click()
    return browser

def click_by_id(browser: WebDriver, id_: str) -> WebDriver:
    btn = browser.find_element(by=By.ID, value=id_)
    btn.click()
    return browser