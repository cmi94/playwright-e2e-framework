import pytest
import allure
import re
import os
from playwright.sync_api import Page, Browser, expect

from locators.common import common_locators
from locators.auth import auth_locators
from utils.utils import login, attach_screenshot
from utils.shoping_order import Shopping_stg, Shoppin_Order
from config import standard_user,standard_user_pw,locked_out_user,locked_out_user_pw


@allure.epic("Checkout 기능")


class Test_checkout:
    page: Page

    @allure.story("checkout")
    @allure.title("SD-checkout-001")
    @allure.description("[결제] 결제 정보 입력 및 확인 페이지 진입 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_checkout_001(self, page:Page):
        with allure.step("Precodition"):
            with allure.step("1. 임의의 상품 장바구니 담긴 상태 "):
                builder = Shoppin_Order()
                builder.setup_stg(page, Shopping_stg.PRODUCT_SELECTED)
                attach_screenshot(page)

            with allure.step("2.  장바구니 페이지 진입 상태 "):
                page.locator(common_locators.CART_BTN).click()
                expect(page.locator("[data-test=\"title\"]")).to_contain_text("Your Cart")
                attach_screenshot(page)

        with allure.step("Test Step 1 :  [Checkout] 버튼 클릭 "):
            page.locator("[data-test=\"checkout\"]").click()
            attach_screenshot(page)

        with allure.step("Expected Result 1 :  결제 정보 입력 페이지 진입 확인 "):
            expect(page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Your Information")
            expect(page.locator("[data-test=\"continue\"]")).to_be_visible()
            attach_screenshot(page)

        with allure.step("Test Step 2 : 결제 정보 입력 후 [Continue] 버튼 클릭 "):
            page.locator("[data-test=\"firstName\"]").fill("Test")
            page.locator("[data-test=\"lastName\"]").fill("User")
            page.locator("[data-test=\"postalCode\"]").fill("12345")
            page.locator("[data-test=\"continue\"]").click()
            attach_screenshot(page)

        with allure.step("Expected Result 2 :  결제 확인 페이지 진입 확인 "):
            expect(page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Overview")
            expect(page.locator("[data-test=\"finish\"]")).to_be_visible()
            expect(page.locator("[data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Backpack")
            expect(page.locator("[data-test=\"inventory-item-price\"]")).to_contain_text("$29.99")
            expect(page.locator("[data-test=\"total-label\"]")).to_contain_text("Total: $32.39")
            attach_screenshot(page)

        with allure.step("Test Step 3 : [Finish] 버튼 클릭 "):
            page.locator("[data-test=\"finish\"]").click()
            attach_screenshot(page)

        with allure.step("Expected Result 3 :  결제 완료 페이지 진입 확인 "):
            expect(page.locator("[data-test=\"title\"]")).to_contain_text("Checkout: Complete!")
            expect(page.locator("[data-test=\"pony-express\"]")).to_be_visible()
            expect(page.locator("[data-test=\"back-to-products\"]")).to_be_visible()
            attach_screenshot(page)

        with allure.step("Test Step 4 : [Back Home] 버튼 클릭 "):
            page.locator("[data-test=\"back-to-products\"]").click()
            attach_screenshot(page)

        with allure.step("Expected Result 4 :  상품 목록 페이지 진입 확인 "):
            expect(page.locator("[data-test=\"title\"]")).to_contain_text("Products")
            attach_screenshot(page)



