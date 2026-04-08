import pytest
import allure
import re
import os
from playwright.sync_api import Page, Browser, expect

from locators.common import common_locators


def login(page, username: str, password: str):
    page.goto(common_locators.BASE_URL)
    page.locator("[data-test=\"username\"]").fill(username)
    page.locator("[data-test=\"password\"]").fill(password)
    page.locator("[data-test=\"login-button\"]").click()


def attach_screenshot(page: Page):
    allure.attach(
        page.screenshot(),
        name="screenshot",
        attachment_type=allure.attachment_type.PNG
    )











































