import pytest
import allure
import re
import os
from playwright.sync_api import Page, Browser, expect

from locators.common import common_locators
from locators.auth import auth_locators
from utils.utils import login, attach_screenshot
from config import standard_user,standard_user_pw,locked_out_user,locked_out_user_pw

@allure.epic("Shopping E2E")

class Test_Shopping_e2e:
    page: Page

    @allure.story("e2e")
    @allure.title("SD-e2e-001")
    @allure.description("[E2E] 상품 선택 및 장바구니 뱃지 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_e2e_001(self, e2e_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                attach_screenshot(e2e_page)

            with allure.step("2. Swag Labs Product 페이지 진입 상태 "):
                expect(e2e_page.locator("[data-test=\"title\"]")).to_be_visible()
                expect(e2e_page.locator("[data-test=\"title\"]")).to_have_text("Products")
                expect(e2e_page.locator(common_locators.SLIDE_BTN)).to_be_visible()
                expect(e2e_page.locator(common_locators.CART_BTN)).to_be_visible()
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1 : 'Sauce Labs Backpack' [Add to cart] 버튼 클릭 "):
            expect(e2e_page.locator("[data-test=\"shopping-cart-link\"]")).to_contain_text("")
            e2e_page.locator("[data-test=\"add-to-cart-sauce-labs-backpack\"]").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1 : 장바구니 아이콘에 '1' 이 표시되는지 확인 "):
            expect(e2e_page.locator("[data-test=\"shopping-cart-link\"]")).to_contain_text("1")
            attach_screenshot(e2e_page)



    @allure.story("e2e")
    @allure.title("SD-e2e-002")
    @allure.description("[E2E] 장바구니 진입 및 상품 노출 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_e2e_002(self, e2e_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                attach_screenshot(e2e_page)

            with allure.step("2. 장바구니에 상품 1개 담긴 상태 "):
                expect(e2e_page.locator("[data-test=\"shopping-cart-link\"]")).to_contain_text("1")
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1 : 장바구니 아이콘 클릭 "):
            e2e_page.locator(common_locators.CART_BTN).click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1 :  'Sauce Labs Backpack' 노출 확인 "):
            expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Your Cart")
            expect(e2e_page.locator("[data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator("[data-test=\"inventory-item-price\"]")).to_contain_text("$29.99")
            attach_screenshot(e2e_page)



    @allure.story("e2e")
    @allure.title("SD-e2e-003")
    @allure.description("[E2E] 결제 정보 입력 및 확인 페이지 진입 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_e2e_003(self, e2e_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                attach_screenshot(e2e_page)

            with allure.step("2.  장바구니 페이지 진입 상태 "):
                expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Your Cart")
                attach_screenshot(e2e_page)

        with allure.step("Test Step 1 :  [Checkout] 버튼 클릭 "):
            e2e_page.locator("[data-test=\"checkout\"]").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 1 :  결제 정보 입력 페이지 진입 확인 "):
            expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Your Information")
            expect(e2e_page.locator("[data-test=\"continue\"]")).to_be_visible()
            attach_screenshot(e2e_page)

        with allure.step("Test Step 2 : 결제 정보 입력 후 [Continue] 버튼 클릭 "):
            e2e_page.locator("[data-test=\"firstName\"]").fill("Test")
            e2e_page.locator("[data-test=\"lastName\"]").fill("User")
            e2e_page.locator("[data-test=\"postalCode\"]").fill("12345")
            e2e_page.locator("[data-test=\"continue\"]").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 2 :  결제 확인 페이지 진입 확인 "):
            expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Overview")
            expect(e2e_page.locator("[data-test=\"finish\"]")).to_be_visible()
            expect(e2e_page.locator("[data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Backpack")
            expect(e2e_page.locator("[data-test=\"inventory-item-price\"]")).to_contain_text("$29.99")
            expect(e2e_page.locator("[data-test=\"total-label\"]")).to_contain_text("Total: $32.39")
            attach_screenshot(e2e_page)

        with allure.step("Test Step 3 : [Finish] 버튼 클릭 "):
            e2e_page.locator("[data-test=\"finish\"]").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 3 :  결제 완료 페이지 진입 확인 "):
            expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Complete!")
            expect(e2e_page.locator("[data-test=\"pony-express\"]")).to_be_visible()
            expect(e2e_page.locator("[data-test=\"back-to-products\"]")).to_be_visible()
            attach_screenshot(e2e_page)

        with allure.step("Test Step 4 : [Back Home] 버튼 클릭 "):
            e2e_page.locator("[data-test=\"back-to-products\"]").click()
            attach_screenshot(e2e_page)

        with allure.step("Expected Result 4 :  상품 목록 페이지 진입 확인 "):
            expect(e2e_page.locator("[data-test=\"title\"]")).to_contain_text("Products")
            attach_screenshot(e2e_page)



