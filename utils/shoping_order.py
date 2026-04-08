from enum import IntEnum

import pytest
import allure
import re
import os
from playwright.sync_api import Page, Browser, expect

from locators.common import common_locators
from locators.auth import auth_locators
from utils.utils import login, attach_screenshot
from config import standard_user,standard_user_pw,locked_out_user,locked_out_user_pw


class Shopping_stg(IntEnum):
    PRODUCT_SELECTED = 1
    ORDER_COMPLETE = 2


class Shoppin_Order:
    def setup_stg (self, e2e_page: Page, stg: Shopping_stg):
        if stg >= Shopping_stg.PRODUCT_SELECTED:
            self.step_1_product_select(e2e_page)
        if stg >= Shopping_stg.ORDER_COMPLETE:
            self.step_2_order_complete(e2e_page)



    def step_1_product_select(self, e2e_page: Page):
        expect(e2e_page.locator("[data-test=\"title\"]")).to_have_text("Products")
        expect(e2e_page.locator(common_locators.SLIDE_BTN)).to_be_visible()
        e2e_page.locator("[data-test=\"add-to-cart-sauce-labs-backpack\"]").click()
        expect(e2e_page.locator("[data-test=\"shopping-cart-link\"]")).to_contain_text("1")
        attach_screenshot(e2e_page)


    def step_2_order_complete(self, e2e_page: Page):
        e2e_page.locator(common_locators.CART_BTN).click()
        expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Your Cart")
        e2e_page.locator("[data-test=\"checkout\"]").click()
        expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Your Information")
        e2e_page.locator("[data-test=\"firstName\"]").fill("Test")
        e2e_page.locator("[data-test=\"lastName\"]").fill("User")
        e2e_page.locator("[data-test=\"postalCode\"]").fill("12345")
        e2e_page.locator("[data-test=\"continue\"]").click()
        expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Overview")
        e2e_page.locator("[data-test=\"finish\"]").click()
        e2e_page.locator("[data-test=\"back-to-products\"]").click()

        attach_screenshot(e2e_page)