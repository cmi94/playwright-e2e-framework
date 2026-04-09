import allure
from playwright.sync_api import Page, expect

from locators.common import CommonLocators
from utils.utils import attach_screenshot


@allure.epic("Shopping E2E")
class TestShoppingE2E:

    @allure.story("E2E")
    @allure.title("SD-E2E-001")
    @allure.description("[E2E] 상품 선택 및 장바구니 뱃지 확인")
    def test_sd_e2e_001(self, e2e_page: Page):
        with allure.step("Precondition"):
            with allure.step("1. standard_user 로그인 상태"):
                attach_screenshot(e2e_page)

            with allure.step("2. 상품 목록 페이지 진입 상태"):
                expect(e2e_page.locator("[data-test='title']")).to_have_text("Products")
                expect(e2e_page.locator(CommonLocators.SLIDE_BTN)).to_be_visible()
                expect(e2e_page.locator(CommonLocators.CART_BTN)).to_be_visible()
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1: 'Sauce Labs Backpack' [Add to cart] 버튼 클릭"):
            e2e_page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1: 장바구니 아이콘에 '1' 표시 확인"):
            expect(e2e_page.locator(CommonLocators.CART_BTN)).to_contain_text("1")
            attach_screenshot(e2e_page)

    @allure.story("E2E")
    @allure.title("SD-E2E-002")
    @allure.description("[E2E] 장바구니 진입 및 상품 노출 확인")
    def test_sd_e2e_002(self, e2e_page: Page):
        with allure.step("Precondition"):
            with allure.step("1. 장바구니에 상품 1개 담긴 상태"):
                expect(e2e_page.locator(CommonLocators.CART_BTN)).to_contain_text("1")
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1: 장바구니 아이콘 클릭"):
            e2e_page.locator(CommonLocators.CART_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1: 장바구니 페이지 진입 및 상품 노출 확인"):
            expect(e2e_page.locator("[data-test='title']")).to_contain_text("Your Cart")
            expect(e2e_page.locator("[data-test='inventory-item-name']")).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator("[data-test='inventory-item-price']")).to_contain_text("$29.99")
            attach_screenshot(e2e_page)

    @allure.story("E2E")
    @allure.title("SD-E2E-003")
    @allure.description("[E2E] 결제 정보 입력 및 주문 완료 확인")
    def test_sd_e2e_003(self, e2e_page: Page):
        with allure.step("Precondition"):
            with allure.step("1. 장바구니 페이지 진입 상태"):
                expect(e2e_page.locator("[data-test='title']")).to_contain_text("Your Cart")
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1: [Checkout] 버튼 클릭"):
            e2e_page.locator("[data-test='checkout']").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1: 결제 정보 입력 페이지 진입 확인"):
            expect(e2e_page.locator("[data-test='title']")).to_contain_text("Checkout: Your Information")
            attach_screenshot(e2e_page)

        with allure.step("Test Step 2: 결제 정보 입력 후 [Continue] 버튼 클릭"):
            e2e_page.locator("[data-test='firstName']").fill("Test")
            e2e_page.locator("[data-test='lastName']").fill("User")
            e2e_page.locator("[data-test='postalCode']").fill("12345")
            e2e_page.locator("[data-test='continue']").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 2: 결제 확인 페이지 진입 확인"):
            expect(e2e_page.locator("[data-test='title']")).to_contain_text("Checkout: Overview")
            expect(e2e_page.locator("[data-test='inventory-item-name']")).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator("[data-test='inventory-item-price']")).to_contain_text("$29.99")
            expect(e2e_page.locator("[data-test='total-label']")).to_contain_text("Total: $32.39")
            attach_screenshot(e2e_page)

        with allure.step("Test Step 3: [Finish] 버튼 클릭"):
            e2e_page.locator("[data-test='finish']").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 3: 주문 완료 페이지 진입 확인"):
            expect(e2e_page.locator("[data-test='title']")).to_contain_text("Checkout: Complete!")
            expect(e2e_page.locator("[data-test='pony-express']")).to_be_visible()
            attach_screenshot(e2e_page)

        with allure.step("Test Step 4: [Back Home] 버튼 클릭"):
            e2e_page.locator("[data-test='back-to-products']").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 4: 상품 목록 페이지 복귀 확인"):
            expect(e2e_page.locator("[data-test='title']")).to_contain_text("Products")
            attach_screenshot(e2e_page)