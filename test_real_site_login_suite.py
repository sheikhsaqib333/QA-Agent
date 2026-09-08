import time
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.automationexercise.com/login"


def unique_email(tag):
    return f"qa.practice.{tag}.{int(time.time())}@example.com"


def submit_signup_form(page: Page, name: str, email: str):
    page.locator("[data-qa=signup-name]").fill(name)
    page.locator("[data-qa=signup-email]").fill(email)
    page.locator("[data-qa=signup-button]").click()


def fill_account_info(page: Page, password="Pass1234"):
    page.locator("#password").fill(password)
    page.locator("#days").select_option("15")
    page.locator("#months").select_option("6")
    page.locator("#years").select_option("1995")
    page.locator("#first_name").fill("Ayesha")
    page.locator("#last_name").fill("Khan")
    page.locator("#address1").fill("123 Test Street")
    page.locator("[data-qa=country]").select_option(label="India")
    page.locator("[data-qa=state]").fill("Punjab")
    page.locator("[data-qa=city]").fill("Lahore")
    page.locator("[data-qa=zipcode]").fill("54000")
    page.locator("[data-qa=mobile_number]").fill("03001234567")


def do_login(page: Page, email: str, password: str):
    page.goto(BASE_URL)
    page.locator("[data-qa=login-email]").fill(email)
    page.locator("[data-qa=login-password]").fill(password)
    page.locator("[data-qa=login-button]").click()


def login_succeeded(page: Page, name: str) -> bool:
    try:
        expect(page.get_by_text(f"Logged in as {name}")).to_be_visible(timeout=4000)
        return True
    except AssertionError:
        return False


@pytest.fixture(scope="module")
def registered_account(browser):
    """Signs up ONE real account, once for this whole file, and reuses it for every login test."""
    name = "Ayesha Khan"
    email = unique_email("logintest")
    password = "Pass1234"

    context = browser.new_context()
    page = context.new_page()
    page.goto(BASE_URL)
    submit_signup_form(page, name, email)
    fill_account_info(page, password=password)
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).to_be_visible()
    page.get_by_text("Continue").click()
    page.get_by_text("Logout").click()
    context.close()

    return {"name": name, "email": email, "password": password}


# ============================================================
# POSITIVE CASES
# ============================================================

# TC-L01 | Critical | Positive
def test_TCL01_login_with_registered_account_succeeds(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])


# TC-L02 | High | Positive
def test_TCL02_logout_returns_to_login_page(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])
    page.get_by_text("Logout").click()
    expect(page.get_by_text("Login to your account")).to_be_visible()


# TC-L03 | Low | Positive
def test_TCL03_repeat_login_same_account(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])
    page.get_by_text("Logout").click()
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])


# TC-L04 | Medium | Positive
def test_TCL04_session_persists_after_reload(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])
    page.reload()
    assert login_succeeded(page, registered_account["name"])


# TC-L05 | Low | Positive
def test_TCL05_enter_key_submits_login(page: Page, registered_account):
    page.goto(BASE_URL)
    page.locator("[data-qa=login-email]").fill(registered_account["email"])
    page.locator("[data-qa=login-password]").fill(registered_account["password"])
    page.locator("[data-qa=login-password]").press("Enter")
    assert login_succeeded(page, registered_account["name"])


# TC-L06 | Low | Positive
def test_TCL06_password_field_is_masked(page: Page):
    page.goto(BASE_URL)
    input_type = page.locator("[data-qa=login-password]").get_attribute("type")
    assert input_type == "password"


# ============================================================
# NEGATIVE CASES
# ============================================================

# TC-L07 | Critical | Negative
def test_TCL07_unregistered_email_rejected(page: Page):
    do_login(page, unique_email("neveregistered"), "SomePassword1")
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()


# TC-L08 | Critical | Negative
def test_TCL08_wrong_password_rejected(page: Page, registered_account):
    do_login(page, registered_account["email"], "WrongPassword1")
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()


# TC-L09 | High | Negative
def test_TCL09_empty_email_blocked(page: Page, registered_account):
    do_login(page, "", registered_account["password"])
    assert not login_succeeded(page, registered_account["name"])


# TC-L10 | High | Negative
def test_TCL10_empty_password_blocked(page: Page, registered_account):
    do_login(page, registered_account["email"], "")
    assert not login_succeeded(page, registered_account["name"])


# TC-L11 | High | Negative
def test_TCL11_both_fields_empty_blocked(page: Page):
    do_login(page, "", "")
    assert not login_succeeded(page, "Ayesha Khan")


# TC-L12 | Medium | Negative
def test_TCL12_invalid_email_format_blocked(page: Page):
    do_login(page, "not-an-email", "SomePassword1")
    assert not login_succeeded(page, "Ayesha Khan")


# TC-L13 | Medium | Negative
def test_TCL13_password_wrong_case_rejected(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"].upper())
    assert not login_succeeded(page, registered_account["name"])


# TC-L14 | Medium | Negative -- direct signup/login connection
def test_TCL14_incomplete_signup_cannot_login(page: Page):
    """Starts a signup but NEVER clicks Create Account -- that email should not be a valid login."""
    email = unique_email("incomplete")
    page.goto(BASE_URL)
    submit_signup_form(page, "Incomplete User", email)
    expect(page.locator("#password")).to_be_visible()
    do_login(page, email, "Pass1234")
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()


# TC-L15 | Medium | Negative (security)
def test_TCL15_sql_injection_attempt_handled_safely(page: Page):
    do_login(page, "' OR '1'='1", "' OR '1'='1")
    assert not login_succeeded(page, "Ayesha Khan")


# TC-L16 | Medium | Negative (security)
def test_TCL16_xss_attempt_handled_safely(page: Page):
    dialog_appeared = {"value": False}

    def handle_dialog(dialog):
        dialog_appeared["value"] = True
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    do_login(page, "<script>alert(1)</script>", "SomePassword1")
    page.wait_for_timeout(1500)
    assert not dialog_appeared["value"], "XSS payload triggered a JS alert -- potential vulnerability!"
    assert not login_succeeded(page, "Ayesha Khan")


# TC-L17 | Low | Negative (exploratory) -- the site appears to trim whitespace from email automatically
def test_TCL17_whitespace_around_email_behavior(page: Page, registered_account):
    do_login(page, f"  {registered_account['email']}  ", registered_account["password"])
    succeeded = login_succeeded(page, registered_account["name"])
    print(f"Login with whitespace-padded email -- succeeded: {succeeded} (informational -- site likely trims input)")


# TC-L18 | Low | Negative
def test_TCL18_whitespace_around_password_rejected(page: Page, registered_account):
    do_login(page, registered_account["email"], f"  {registered_account['password']}  ")
    assert not login_succeeded(page, registered_account["name"])


# TC-L19 | Low | Negative
def test_TCL19_extremely_long_input_handled_gracefully(page: Page):
    long_email = "a" * 300 + "@example.com"
    long_password = "b" * 300
    do_login(page, long_email, long_password)
    assert not login_succeeded(page, "Ayesha Khan")


# TC-L20 | Low | Negative (exploratory)
def test_TCL20_whitespace_only_email(page: Page):
    do_login(page, "   ", "SomePassword1")
    succeeded = login_succeeded(page, "Ayesha Khan")
    print(f"Login with whitespace-only email -- succeeded: {succeeded} (informational)")


# TC-L21 | Low | Positive/exploratory
def test_TCL21_uppercase_email_login(page: Page, registered_account):
    do_login(page, registered_account["email"].upper(), registered_account["password"])
    succeeded = login_succeeded(page, registered_account["name"])
    print(f"Login with uppercase email -- succeeded: {succeeded} (informational)")


# TC-L22 | Low | Exploratory
def test_TCL22_visit_login_page_while_authenticated(page: Page, registered_account):
    do_login(page, registered_account["email"], registered_account["password"])
    assert login_succeeded(page, registered_account["name"])
    page.goto(BASE_URL)
    still_shows_login_form = page.get_by_text("Login to your account").is_visible()
    print(f"Login form still shown while already authenticated: {still_shows_login_form} (informational)")


# ============================================================
# ACCOUNT LIFECYCLE -- signup + login + delete, connected
# ============================================================

def signup_full_account(page: Page, name: str, email: str, password: str = "Pass1234"):
    """Signs up a brand new account, all the way through, ending logged in."""
    page.goto(BASE_URL)
    submit_signup_form(page, name, email)
    fill_account_info(page, password=password)
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).to_be_visible()
    page.get_by_text("Continue").click()


def delete_account(page: Page):
    """Deletes the currently logged-in account and confirms the deletion screen."""
    page.get_by_text("Delete Account").click()
    expect(page.get_by_text("ACCOUNT DELETED!")).to_be_visible()
    page.get_by_text("Continue").click()


# TC-L23 | Critical | Negative -- signup/login/delete connection
def test_TCL23_login_fails_after_account_deleted(page: Page):
    name = "Ayesha Khan"
    email = unique_email("tcl23")
    password = "Pass1234"

    signup_full_account(page, name, email, password)  # creates the account and logs in
    delete_account(page)                                # deletes it, returns to Login/Signup page

    do_login(page, email, password)
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()


# TC-L24 | High | Positive -- signup/login/delete connection
def test_TCL24_can_resignup_with_email_after_deletion(page: Page):
    name = "Ayesha Khan"
    email = unique_email("tcl24")
    password = "Pass1234"

    signup_full_account(page, name, email, password)
    delete_account(page)

    # The email should now be free again -- signing up with it should NOT say "already exist"
    page.goto(BASE_URL)
    submit_signup_form(page, name, email)
    expect(page.locator("#password")).to_be_visible()
