import allure
from playwright.sync_api import Page, expect

from locators.common import CommonLocators
from locators.inventory import InventoryLocators
from locators.cart import CartLocators
from locators.checkout import CheckoutLocators
from utils.utils import attach_screenshot

"""
E2E Shopping Flow Tests
 
연속된 사용자 프로세스(상품 선택 → 장바구니 → 주문 완료)는 단일 브라우저 세션에서 검증합니다.
 
[설계 의도]
본 파일의 TC들은 session scope fixture(`e2e_page`)를 공유하여 순차적으로 실행됩니다.
이는 pytest의 일반적인 "테스트 격리" 원칙과 다른 선택으로, 다음 이유에서 의도된 구조입니다:
 
1. 실제 사용자는 상품 선택부터 주문 완료까지 단일 세션에서 이어서 수행합니다.
   연속 플로우에서 발생할 수 있는 상태 전이 이슈(세션 만료, 장바구니 초기화 등)를
   검증하려면 세션을 공유하는 구조가 필요합니다.
 
2. 단위 기능 검증(로그인, 결제 등)은 `test_login.py`, `test_checkout.py`에서
   function scope + ShoppingOrder(data_builder) 패턴으로 독립적으로 수행합니다.
 
즉, 본 프레임워크는 "독립 기능 TC는 function scope", "연속적인 프로세스 TC는 session scope"로
목적에 따라 fixture scope를 분리하여 사용합니다.
"""


@allure.epic("Shopping E2E")
@allure.feature("쇼핑 E2E 프로세스")
class TestShoppingE2E:

    @allure.story("E2E")
    @allure.title("SD-E2E-001")
    @allure.description("[E2E] 상품 선택 및 장바구니 뱃지 확인")
    def test_sd_e2e_001(self, e2e_page: Page):
        with allure.step("Precondition"):
            with allure.step("1. standard_user 로그인 상태"):
                attach_screenshot(e2e_page)

            with allure.step("2. 상품 목록 페이지 진입 상태"):
                expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_have_text("Products")
                expect(e2e_page.locator(CommonLocators.SLIDE_BTN)).to_be_visible()
                expect(e2e_page.locator(CommonLocators.CART_BTN)).to_be_visible()
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1: 'Sauce Labs Backpack' [Add to cart] 버튼 클릭"):
            e2e_page.locator(InventoryLocators.ADD_TO_CART_BACKPACK).click()
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
            expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Your Cart")
            expect(e2e_page.locator(InventoryLocators.ITEM_NAME)).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator(InventoryLocators.ITEM_PRICE)).to_contain_text("$29.99")
            attach_screenshot(e2e_page)

    @allure.story("E2E")
    @allure.title("SD-E2E-003")
    @allure.description("[E2E] 결제 정보 입력 및 주문 완료 확인")
    def test_sd_e2e_003(self, e2e_page: Page):
        with allure.step("Precondition"):
            with allure.step("1. 장바구니 페이지 진입 상태"):
                expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Your Cart")
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1: [Checkout] 버튼 클릭"):
            e2e_page.locator(CartLocators.CHECKOUT_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1: 결제 정보 입력 페이지 진입 확인"):
            expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Your Information")
            attach_screenshot(e2e_page)

        with allure.step("Test Step 2: 결제 정보 입력 후 [Continue] 버튼 클릭"):
            e2e_page.locator(CheckoutLocators.FIRST_NAME).fill("Test")
            e2e_page.locator(CheckoutLocators.LAST_NAME).fill("User")
            e2e_page.locator(CheckoutLocators.POSTAL_CODE).fill("12345")
            e2e_page.locator(CheckoutLocators.CONTINUE_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 2: 결제 확인 페이지 진입 확인"):
            expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Overview")
            expect(e2e_page.locator(InventoryLocators.ITEM_NAME)).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator(InventoryLocators.ITEM_PRICE)).to_contain_text("$29.99")
            expect(e2e_page.locator(CheckoutLocators.TOTAL_LABEL)).to_contain_text("Total: $32.39")
            attach_screenshot(e2e_page)

        with allure.step("Test Step 3: [Finish] 버튼 클릭"):
            e2e_page.locator(CheckoutLocators.FINISH_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 3: 주문 완료 페이지 진입 확인"):
            expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Checkout: Complete!")
            expect(e2e_page.locator(CheckoutLocators.PONY_EXPRESS)).to_be_visible()
            attach_screenshot(e2e_page)

        with allure.step("Test Step 4: [Back Home] 버튼 클릭"):
            e2e_page.locator(CheckoutLocators.BACK_TO_PRODUCTS_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 4: 상품 목록 페이지 복귀 확인"):
            expect(e2e_page.locator(InventoryLocators.PAGE_TITLE)).to_contain_text("Products")
            attach_screenshot(e2e_page)