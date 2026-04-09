import allure
from playwright.sync_api import Page

from locators.auth import AuthLocators
from locators.common import CommonLocators


def login(page: Page, username: str, password: str):
    page.goto(CommonLocators.BASE_URL)
    page.locator(AuthLocators.USERNAME).fill(username)
    page.locator(AuthLocators.PASSWORD).fill(password)
    page.locator(AuthLocators.LOGIN_BTN).click()


def attach_screenshot(page: Page):
    allure.attach(
        page.screenshot(),
        name="screenshot",
        attachment_type=allure.attachment_type.PNG
    )