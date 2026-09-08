import pytest
from playwright.sync_api import Page, expect
from pages.signup_page import SignupPage

FILE_PATH = "file:///C:/Users/Terafort/Desktop/my-automation/login-signup-practice.html"  # <-- update to your real path


@pytest.fixture
def signup_page(page: Page):
    sp = SignupPage(page)
    sp.goto(FILE_PATH)
    return sp


# TC-01 | Critical | Positive
def test_TC01_signup_success(signup_page):
    signup_page.signup("Ayesha Khan", "ayesha.khan@example.com", "Pass1234", "Pass1234")
    expect(signup_page.success_banner()).to_be_visible()
    expect(signup_page.success_banner()).to_contain_text("Account created")


# TC-02 | Critical | Negative
def test_TC02_duplicate_email(signup_page):
    signup_page.signup("Someone Else", "test@example.com", "Pass1234", "Pass1234")
    expect(signup_page.error_banner()).to_be_visible()
    expect(signup_page.error_banner()).to_contain_text("already registered")


# TC-03 | High | Negative
def test_TC03_password_mismatch(signup_page):
    signup_page.signup("Bilal Ahmed", "bilal@example.com", "Pass1234", "Different99")
    expect(signup_page.confirm_password_error()).to_be_visible()
    expect(signup_page.confirm_password_error()).to_contain_text("do not match")


# TC-04 | High | Negative
def test_TC04_short_password(signup_page):
    signup_page.signup("Sara Ali", "sara@example.com", "abc1", "abc1")
    expect(signup_page.password_error()).to_be_visible()


# TC-05 | High | Negative
def test_TC05_terms_unchecked(signup_page):
    signup_page.signup("Usman Tariq", "usman@example.com", "Pass1234", "Pass1234", check_terms=False)
    expect(signup_page.error_banner()).to_be_visible()
    expect(signup_page.error_banner()).to_contain_text("Terms of Service")


# TC-06 | Medium | Negative
def test_TC06_invalid_email_format(signup_page):
    signup_page.signup("Hina Malik", "not-an-email", "Pass1234", "Pass1234")
    expect(signup_page.email_error()).to_be_visible()
    expect(signup_page.email_error()).to_contain_text("valid email")


# TC-07 | Medium | Negative
def test_TC07_short_name(signup_page):
    signup_page.signup("A", "shortname@example.com", "Pass1234", "Pass1234")
    expect(signup_page.fullname_error()).to_be_visible()


# TC-08 | Medium | Negative
def test_TC08_password_no_number(signup_page):
    signup_page.signup("Fahad Iqbal", "fahad@example.com", "OnlyLetters", "OnlyLetters")
    expect(signup_page.password_error()).to_be_visible()


# TC-09 | Medium | Negative
def test_TC09_password_no_letter(signup_page):
    signup_page.signup("Zara Sheikh", "zara@example.com", "12345678", "12345678")
    expect(signup_page.password_error()).to_be_visible()


# TC-10 | Low | Positive
def test_TC10_error_clears_on_retry(signup_page):
    signup_page.signup("A", "retry@example.com", "Pass1234", "Pass1234")
    expect(signup_page.fullname_error()).to_be_visible()

    signup_page.fill_name("Retry Person")
    signup_page.submit()

    expect(signup_page.success_banner()).to_be_visible()
    expect(signup_page.fullname_error()).to_be_hidden()
