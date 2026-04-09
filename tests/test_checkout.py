import allure
from playwright.sync_api import Page, expect

from locators.common import CommonLocators
from locators.inventory import InventoryLocators
from locators.cart import CartLocators
from locators.checkout import CheckoutLocators
from utils.utils import attach_screenshot
from utils.shopping_order import ShoppingStage, ShoppingOrder


@allure.epic("Checkout 기능")
class TestCheckout:

    @allure.story("Checkout")
    @allure.title("SD-CHECKOUT-001")
    @allure.description("[Checkout] 결제 정보 입력 및 주문 완료 확인")
    def test_sd_checkout_001(self, page: Page):
        with allure.step("Precondition"):
            with allure.step("1. 장바구니에 상품 담긴 상태 (data_builder 세팅)"):
                builder = ShoppingOrder()
                builder.setup_stage(page, ShoppingStage.PRODUCT_SELECTED)
                attach_screenshot(page)

            with allure.step("2. 장바구니 페이지 진입"):
                page.locator(CommonLocators.CART_BTN).click()
                expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Your Cart")
                attach_screenshot(page)

        with allure.step("Test Step 1: [Checkout] 버튼 클릭"):
            page.locator(CartLocators.CHECKOUT_BTN).click()
            attach_screenshot(page)

        with allure.step("Expected Result 1: 결제 정보 입력 페이지 진입 확인"):
            expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Your Information")
            expect(page.locator(CheckoutLocators.CONTINUE_BTN)).to_be_visible()
            attach_screenshot(page)

        with allure.step("Test Step 2: 결제 정보 입력 후 [Continue] 버튼 클릭"):
            page.locator(CheckoutLocators.FIRST_NAME).fill("Test")
            page.locator(CheckoutLocators.LAST_NAME).fill("User")
            page.locator(CheckoutLocators.POSTAL_CODE).fill("12345")
            page.locator(CheckoutLocators.CONTINUE_BTN).click()
            attach_screenshot(page)

        with allure.step("Expected Result 2: 결제 확인 페이지 진입 확인"):
            expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Overview")
            expect(page.locator(CheckoutLocators.FINISH_BTN)).to_be_visible()
            expect(page.locator(InventoryLocators.ITEM_NAME)).to_contain_text("Sauce Labs Backpack")
            expect(page.locator(InventoryLocators.ITEM_PRICE)).to_contain_text("$29.99")
            expect(page.locator(CheckoutLocators.TOTAL_LABEL)).to_contain_text("Total: $32.39")
            attach_screenshot(page)

        with allure.step("Test Step 3: [Finish] 버튼 클릭"):
            page.locator(CheckoutLocators.FINISH_BTN).click()
            attach_screenshot(page)

        with allure.step("Expected Result 3: 주문 완료 페이지 진입 확인"):
            expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Complete!")
            expect(page.locator(CheckoutLocators.PONY_EXPRESS)).to_be_visible()
            expect(page.locator(CheckoutLocators.BACK_TO_PRODUCTS_BTN)).to_be_visible()
            attach_screenshot(page)

        with allure.step("Test Step 4: [Back Home] 버튼 클릭"):
            page.locator(CheckoutLocators.BACK_TO_PRODUCTS_BTN).click()
            attach_screenshot(page)

        with allure.step("Expected Result 4: 상품 목록 페이지 복귀 확인"):
            expect(page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Products")
            attach_screenshot(page)