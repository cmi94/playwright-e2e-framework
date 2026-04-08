import pytest
from utils.utils import login
from playwright.sync_api import Page
from config import standard_user, standard_user_pw
from locators.common import common_locators


# headless 옵션 설정
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args}


@pytest.fixture(scope="session")
def e2e_page(browser):
    page = browser.new_page()
    login(page, standard_user, standard_user_pw)
    yield page
    page.close()


@pytest.fixture(scope="function")
def login_page(browser):
    page = browser.new_page()
    page.goto(common_locators.BASE_URL)
    yield page
    page.close()


@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    login(page, standard_user, standard_user_pw)
    yield page
    page.close()