import allure
from playwright.sync_api import Page

from locators.common import CommonLocators


def login(page: Page, username: str, password: str):
    page.goto(CommonLocators.BASE_URL)
    page.locator(CommonLocators.USERNAME_INPUT).fill(username)
    page.locator(CommonLocators.PASSWORD_INPUT).fill(password)
    page.locator(CommonLocators.LOGIN_BTN).click()


def attach_screenshot(page: Page):
    allure.attach(
        page.screenshot(),
        name="screenshot",
        attachment_type=allure.attachment_type.PNG
    )