from enum import IntEnum
from playwright.sync_api import Page, expect

from locators.common import CommonLocators
from utils.utils import attach_screenshot


class ShoppingStage(IntEnum):
    PRODUCT_SELECTED = 1
    ORDER_COMPLETE = 2


class ShoppingOrder:
    def setup_stage(self, page: Page, stage: ShoppingStage):
        if stage >= ShoppingStage.PRODUCT_SELECTED:
            self._step_select_product(page)
        if stage >= ShoppingStage.ORDER_COMPLETE:
            self._step_complete_order(page)

    def _step_select_product(self, page: Page):
        expect(page.locator("[data-test='title']")).to_have_text("Products")
        expect(page.locator(CommonLocators.SLIDE_BTN)).to_be_visible()
        page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
        expect(page.locator(CommonLocators.CART_BTN)).to_contain_text("1")
        attach_screenshot(page)

    def _step_complete_order(self, page: Page):
        page.locator(CommonLocators.CART_BTN).click()
        expect(page.locator("[data-test='title']")).to_contain_text("Your Cart")
        page.locator("[data-test='checkout']").click()
        expect(page.locator("[data-test='title']")).to_contain_text("Checkout: Your Information")
        page.locator("[data-test='firstName']").fill("Test")
        page.locator("[data-test='lastName']").fill("User")
        page.locator("[data-test='postalCode']").fill("12345")
        page.locator("[data-test='continue']").click()
        expect(page.locator("[data-test='title']")).to_contain_text("Checkout: Overview")
        page.locator("[data-test='finish']").click()
        page.locator("[data-test='back-to-products']").click()
        attach_screenshot(page)