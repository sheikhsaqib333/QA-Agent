import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

FILE_PATH = "file:///C:/Users/Terafort/Desktop/my-automation/login-signup-practice.html"  # <-- update to your real path


@pytest.fixture
def login_page(page: Page):
    lp = LoginPage(page)
    lp.goto(FILE_PATH)
    return lp


# TC-11 | Critical | Positive
def test_TC11_login_success(login_page):
    login_page.login("test@example.com", "Test1234")
    expect(login_page.dashboard_welcome()).to_be_visible()
    expect(login_page.dashboard_welcome()).to_contain_text("Welcome back")


# TC-12 | Critical | Negative
def test_TC12_wrong_password(login_page):
    login_page.login("test@example.com", "WrongPass1")
    expect(login_page.banner()).to_be_visible()
    expect(login_page.banner()).to_contain_text("Invalid email or password")


# TC-13 | Critical | Negative
def test_TC13_account_lockout(login_page):
    for attempt in range(5):
        login_page.login("test@example.com", "WrongPass1")
    login_page.login("test@example.com", "WrongPass1")
    expect(login_page.banner()).to_contain_text("locked")


# TC-14 | High | Negative
def test_TC14_empty_email(login_page):
    login_page.login("", "Test1234")
    expect(login_page.email_error()).to_be_visible()
    expect(login_page.email_error()).to_contain_text("required")


# TC-15 | High | Negative
def test_TC15_empty_password(login_page):
    login_page.login("test@example.com", "")
    expect(login_page.password_error()).to_be_visible()
    expect(login_page.password_error()).to_contain_text("required")


# TC-16 | High | Positive
def test_TC16_logout_returns_to_login(login_page):
    login_page.login("test@example.com", "Test1234")
    expect(login_page.dashboard_welcome()).to_be_visible()

    login_page.logout()
    expect(login_page.email_input()).to_be_visible()
    expect(login_page.email_input()).to_have_value("")


# TC-17 | Medium | Negative
def test_TC17_invalid_email_format(login_page):
    login_page.login("not-an-email", "Test1234")
    expect(login_page.email_error()).to_be_visible()
    expect(login_page.email_error()).to_contain_text("valid email")


# TC-18 | Medium | Positive (signup -> login integration)
def test_TC18_new_account_can_login(page: Page):
    from pages.signup_page import SignupPage

    signup_page = SignupPage(page)
    signup_page.goto(FILE_PATH)
    signup_page.signup("Newly Signed Up", "newuser@example.com", "NewPass1", "NewPass1")
    expect(signup_page.success_banner()).to_be_visible()

    login_page = LoginPage(page)
    login_page.switch_to_login_tab()
    login_page.login("newuser@example.com", "NewPass1")
    expect(login_page.dashboard_welcome()).to_be_visible()


# TC-19 | Low | Positive
def test_TC19_no_stale_errors_across_tabs(login_page):
    login_page.login("", "")
    expect(login_page.email_error()).to_be_visible()

    login_page.switch_to_signup_tab()
    login_page.switch_to_login_tab()

    expect(login_page.email_error()).to_be_hidden()
