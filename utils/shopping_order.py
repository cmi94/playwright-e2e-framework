from enum import IntEnum
from playwright.sync_api import Page, expect

from locators.common import CommonLocators
from locators.inventory import InventoryLocators
from locators.cart import CartLocators
from locators.checkout import CheckoutLocators
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
        expect(page.locator(InventoryLocators.PAGE_TITLE)).to_have_text("Products")
        expect(page.locator(CommonLocators.SLIDE_BTN)).to_be_visible()
        page.locator(InventoryLocators.ADD_TO_CART_BACKPACK).click()
        expect(page.locator(CommonLocators.CART_BTN)).to_contain_text("1")
        attach_screenshot(page)

    def _step_complete_order(self, page: Page):
        page.locator(CommonLocators.CART_BTN).click()
        expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Your Cart")
        page.locator(CartLocators.CHECKOUT_BTN).click()
        expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Your Information")
        page.locator(CheckoutLocators.FIRST_NAME).fill("Test")
        page.locator(CheckoutLocators.LAST_NAME).fill("User")
        page.locator(CheckoutLocators.POSTAL_CODE).fill("12345")
        page.locator(CheckoutLocators.CONTINUE_BTN).click()
        expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Overview")
        page.locator(CheckoutLocators.FINISH_BTN).click()
        page.locator(CheckoutLocators.BACK_TO_PRODUCTS_BTN).click()
        attach_screenshot(page)