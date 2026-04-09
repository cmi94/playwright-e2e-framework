import pytest
from utils.utils import login
from playwright.sync_api import Page
from config import STANDARD_USER, STANDARD_USER_PW
from locators.common import CommonLocators


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args}


@pytest.fixture(scope="session")
def e2e_page(browser):
    page = browser.new_page()
    login(page, STANDARD_USER, STANDARD_USER_PW)
    yield page
    page.close()


@pytest.fixture(scope="function")
def login_page(browser):
    page = browser.new_page()
    page.goto(CommonLocators.BASE_URL)
    yield page
    page.close()


@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    login(page, STANDARD_USER, STANDARD_USER_PW)
    yield page
    page.close()