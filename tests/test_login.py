import pytest
import allure
import re
import os
from playwright.sync_api import Page, Browser, expect

from locators.common import common_locators
from locators.auth import auth_locators
from utils.utils import login, attach_screenshot
from config import standard_user,standard_user_pw,locked_out_user,locked_out_user_pw

@allure.epic("Login 기능")

class Test_login:
    page: Page

    @allure.story("Auth")
    @allure.title("SD-LOGIN-001")
    @allure.description("[Auth] 정상 로그인 및 상품 목록 페이지 진입 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_login_001(self, login_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                expect(login_page.get_by_text("Swag Labs")).to_be_visible()
                attach_screenshot(login_page)

        with allure.step("Test Step 1 :  Username 입력란에 'standard_user' 입력"):
            login_page.locator(auth_locators.USERNAME).fill("standard_user")
            attach_screenshot(login_page)

        with allure.step("Expected Result 1 : Username 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.USERNAME)).to_have_value(standard_user)
            attach_screenshot(login_page)

        with allure.step("Test Step 2 : Password 입력란에 'secret_sauce' 입력"):
            login_page.locator(auth_locators.PASSWORD).fill("secret_sauce")
            attach_screenshot(login_page)

        with allure.step("Expected Result 2 : Password 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.PASSWORD)).to_have_value(standard_user_pw)
            attach_screenshot(login_page)

        with allure.step("Test Step 3 : Login 버튼 클릭"):
            login_page.locator(auth_locators.LOGIN_BTN).click()
            attach_screenshot(login_page)

        with allure.step("Expected Result 3 : 상품 목록 페이지 진입 확인"):
            expect(login_page.get_by_text("Products")).to_be_visible()
            attach_screenshot(login_page)



    @allure.story("Auth")
    @allure.title("SD-LOGIN-002")
    @allure.description("[Auth] ID 미입력 시 오류 메시지 노출 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_login_002(self, login_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                expect(login_page.get_by_text("Swag Labs")).to_be_visible()
                attach_screenshot(login_page)

        with allure.step("Test Step 1 :  Username 입력란에 '공란' 유지"):
            login_page.locator(auth_locators.USERNAME).fill("")
            attach_screenshot(login_page)

        with allure.step("Expected Result 1 : Username 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.USERNAME)).to_have_value("")
            attach_screenshot(login_page)

        with allure.step("Test Step 2 : Password 입력란에 'secret_sauce' 입력"):
            login_page.locator(auth_locators.PASSWORD).fill("secret_sauce")
            attach_screenshot(login_page)

        with allure.step("Expected Result 2 : Password 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.PASSWORD)).to_have_value(standard_user_pw)
            attach_screenshot(login_page)

        with allure.step("Test Step 3 : Login 버튼 클릭"):
            login_page.locator(auth_locators.LOGIN_BTN).click()
            attach_screenshot(login_page)

        with allure.step("Expected Result 3 : 상품 목록 페이지 진입 확인"):
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_be_visible()
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_have_text("Epic sadface: Username is required")
            attach_screenshot(login_page)


    @allure.story("Auth")
    @allure.title("SD-LOGIN-003")
    @allure.description("[Auth] PW 미입력 시 오류 메시지 노출 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_login_003(self, login_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                expect(login_page.get_by_text("Swag Labs")).to_be_visible()
                attach_screenshot(login_page)

        with allure.step("Test Step 1 :  Username 입력란에 'standard_user' 입력"):
            login_page.locator(auth_locators.USERNAME).fill(standard_user)
            attach_screenshot(login_page)

        with allure.step("Expected Result 1 : Username 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.USERNAME)).to_have_value(standard_user)
            attach_screenshot(login_page)

        with allure.step("Test Step 2 : Password 입력란에 '공란' 유지"):
            login_page.locator(auth_locators.PASSWORD).fill("")
            attach_screenshot(login_page)

        with allure.step("Expected Result 2 : Password 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.PASSWORD)).to_have_value("")
            attach_screenshot(login_page)

        with allure.step("Test Step 3 : Login 버튼 클릭"):
            login_page.locator(auth_locators.LOGIN_BTN).click()
            attach_screenshot(login_page)

        with allure.step("Expected Result 3 : 상품 목록 페이지 진입 확인"):
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_be_visible()
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_have_text("Epic sadface: Password is required")
            attach_screenshot(login_page)


    @allure.story("Auth")
    @allure.title("SD-LOGIN-004")
    @allure.description("[Auth] PW 오류 시 오류 메시지 노출 확인")
    @allure.link(url="https://polaqube.atlassian.net/browse/LIMS-1446", name="JIRA")
    def test_sd_login_004(self, login_page:Page):
        with allure.step("Precodition"):
            with allure.step("1. https://www.saucedemo.com 진입 상태 "):
                expect(login_page.get_by_text("Swag Labs")).to_be_visible()
                attach_screenshot(login_page)

        with allure.step("Test Step 1 :  Username 입력란에 'standard_user' 입력"):
            login_page.locator(auth_locators.USERNAME).fill(standard_user)
            attach_screenshot(login_page)

        with allure.step("Expected Result 1 : Username 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.USERNAME)).to_have_value(standard_user)
            attach_screenshot(login_page)

        with allure.step("Test Step 2 : Password 입력란에 '잘못된 비밀번호' 입력"):
            login_page.locator(auth_locators.PASSWORD).fill(locked_out_user_pw)
            attach_screenshot(login_page)

        with allure.step("Expected Result 2 : Password 입력 가능한 것 확인"):
            expect(login_page.locator(auth_locators.PASSWORD)).to_have_value(locked_out_user_pw)
            attach_screenshot(login_page)

        with allure.step("Test Step 3 : Login 버튼 클릭"):
            login_page.locator(auth_locators.LOGIN_BTN).click()
            attach_screenshot(login_page)

        with allure.step("Expected Result 3 : 상품 목록 페이지 진입 확인"):
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_be_visible()
            expect(login_page.locator(auth_locators.ERROR_MSG)).to_have_text("Epic sadface: Username and password do not match any user in this service")
            attach_screenshot(login_page)
