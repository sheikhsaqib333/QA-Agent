import os
import time
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.automationexercise.com/login"
VALID_COUNTRIES = ["India", "United States", "Canada", "Australia", "Israel", "New Zealand", "Singapore"]

os.makedirs("screenshots", exist_ok=True)


def unique_email(tag):
    """Builds a unique email each run using the current time, so repeat runs never collide."""
    return f"qa.practice.{tag}.{int(time.time())}@example.com"


def go_to_signup_form(page: Page):
    page.goto(BASE_URL)


def submit_signup_form(page: Page, name: str, email: str):
    page.locator("[data-qa=signup-name]").fill(name)
    page.locator("[data-qa=signup-email]").fill(email)
    page.locator("[data-qa=signup-button]").click()


def on_account_info_page(page: Page) -> bool:
    """Returns True if we actually advanced to the Account Information page."""
    try:
        expect(page.locator("#password")).to_be_visible(timeout=4000)
        return True
    except AssertionError:
        return False


def fill_account_info(page: Page, country="India", password="Pass1234", mobile="03001234567",
                       first_name="Ayesha", last_name="Khan", address1="123 Test Street",
                       state="Punjab", city="Lahore", zipcode="54000",
                       fill_company=False, fill_address2=False,
                       check_newsletter=False, check_offers=False, title=None):
    if title == "Mrs":
        page.locator("#id_gender2").check()
    elif title == "Mr":
        page.locator("#id_gender1").check()

    page.locator("#password").fill(password)
    page.locator("#days").select_option("15")
    page.locator("#months").select_option("6")
    page.locator("#years").select_option("1995")

    if check_newsletter:
        page.locator("#newsletter").check()
    if check_offers:
        page.locator("#optin").check()

    page.locator("#first_name").fill(first_name)
    page.locator("#last_name").fill(last_name)
    if fill_company:
        page.locator("#company").fill("Test Company")
    page.locator("#address1").fill(address1)
    if fill_address2:
        page.locator("#address2").fill("Apartment 4B")

    page.locator("[data-qa=country]").select_option(label=country)
    page.locator("[data-qa=state]").fill(state)
    page.locator("[data-qa=city]").fill(city)
    page.locator("[data-qa=zipcode]").fill(zipcode)
    page.locator("[data-qa=mobile_number]").fill(mobile)


def complete_signup_and_logout(page: Page, name: str = "Ayesha Khan", screenshot_tag: str = None):
    """After a successful signup: screenshot the confirmation, confirm login worked, then log out."""
    expect(page.get_by_text("ACCOUNT CREATED!")).to_be_visible()
    if screenshot_tag:
        page.screenshot(path=f"screenshots/{screenshot_tag}_account_created.png")
    page.get_by_text("Continue").click()
    expect(page.get_by_text(f"Logged in as {name}")).to_be_visible()
    page.get_by_text("Logout").click()


# ============================================================
# STEP 1 -- Name / Email form
# ============================================================

# TC-R01 | Critical | Positive
def test_TCR01_valid_signup_reaches_account_info(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr01"))
    assert on_account_info_page(page)
    page.screenshot(path="screenshots/TCR01_account_info_page.png")


# TC-R02 | Critical | Negative
def test_TCR02_duplicate_email_rejected(page: Page):
    email = unique_email("tcr02")
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", email)
    assert on_account_info_page(page)
    fill_account_info(page)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, "Ayesha Khan", screenshot_tag="TCR02_first_signup")

    go_to_signup_form(page)
    submit_signup_form(page, "Someone Else", email)
    expect(page.get_by_text("Email Address already exist!")).to_be_visible()
    page.screenshot(path="screenshots/TCR02_duplicate_email_rejected.png")


# TC-R03 | Medium | Negative
def test_TCR03_empty_name_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "", unique_email("tcr03"))
    assert not on_account_info_page(page)
    page.wait_for_timeout(2500)


# TC-R04 | Medium | Negative
def test_TCR04_empty_email_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", "")
    assert not on_account_info_page(page)
    page.wait_for_timeout(2500)


# TC-R05 | Medium | Negative
def test_TCR05_invalid_email_format_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", "not-an-email")
    assert not on_account_info_page(page)
    page.wait_for_timeout(2500)


# TC-R06 | Low | Negative -- DISCOVERED BUG: the site's "required" validation only checks for a
# completely empty field, not whitespace. A name of just spaces is incorrectly accepted.
# This test documents that real behavior instead of asserting the (wrong) ideal behavior.
def test_TCR06_whitespace_only_name_is_incorrectly_accepted(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "   ", unique_email("tcr06"))
    assert on_account_info_page(page)  # BUG: this SHOULD be blocked, like TC-R03
    print("KNOWN ISSUE: whitespace-only name is accepted -- should be rejected like an empty name")
    page.screenshot(path="screenshots/TCR06_KNOWN_BUG_whitespace_name_accepted.png")


# TC-R07 | Low | Positive
def test_TCR07_name_with_special_characters_accepted(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Anne-Marie O'Brien", unique_email("tcr07"))
    assert on_account_info_page(page)


# TC-R08 | Low | Positive
def test_TCR08_very_long_name_accepted(page: Page):
    go_to_signup_form(page)
    long_name = "Ayesha " + ("Khan" * 25)
    submit_signup_form(page, long_name, unique_email("tcr08"))
    assert on_account_info_page(page)


# TC-R09 | Low | Positive
def test_TCR09_mixed_case_email_accepted(page: Page):
    go_to_signup_form(page)
    email = unique_email("TCR09").upper().replace("@EXAMPLE.COM", "@example.com")
    submit_signup_form(page, "Ayesha Khan", email)
    assert on_account_info_page(page)


# ============================================================
# STEP 2 -- Account Information page
# ============================================================

# TC-R10 | Critical | Positive
def test_TCR10_all_required_valid_optional_blank_succeeds(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr10"))
    fill_account_info(page)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag="TCR10")


# TC-R11 | Critical | Positive (data-driven across every supported country)
@pytest.mark.parametrize("country", VALID_COUNTRIES)
def test_TCR11_signup_succeeds_for_every_country(page: Page, country):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email(f"tcr11-{country.replace(' ', '')}"))
    fill_account_info(page, country=country)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag=f"TCR11_{country.replace(' ', '')}")


# TC-R12 | High | Negative
def test_TCR12_empty_password_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr12"))
    fill_account_info(page, password="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R13 | High | Negative
def test_TCR13_empty_first_name_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr13"))
    fill_account_info(page, first_name="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R14 | High | Negative
def test_TCR14_empty_last_name_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr14"))
    fill_account_info(page, last_name="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R15 | High | Negative
def test_TCR15_empty_address_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr15"))
    fill_account_info(page, address1="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R16 | High | Negative
def test_TCR16_empty_state_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr16"))
    fill_account_info(page, state="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R17 | High | Negative
def test_TCR17_empty_city_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr17"))
    fill_account_info(page, city="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R18 | High | Negative
def test_TCR18_empty_zipcode_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr18"))
    fill_account_info(page, zipcode="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R19 | High | Negative
def test_TCR19_empty_mobile_number_blocked(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr19"))
    fill_account_info(page, mobile="")
    page.locator("[data-qa=create-account]").click()
    expect(page.get_by_text("ACCOUNT CREATED!")).not_to_be_visible()
    page.wait_for_timeout(2500)


# TC-R20 | Medium | Negative (exploratory -- documents actual behavior either way)
def test_TCR20_mobile_number_with_letters(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr20"))
    fill_account_info(page, mobile="abcde12345")
    page.locator("[data-qa=create-account]").click()
    created = page.get_by_text("ACCOUNT CREATED!").is_visible()
    print(f"Mobile with letters -- account created: {created} (informational, not a hard pass/fail)")


# TC-R21 | Low | Positive
def test_TCR21_newsletter_and_offers_checked_succeeds(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr21"))
    fill_account_info(page, check_newsletter=True, check_offers=True)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag="TCR21")


# TC-R22 | Low | Positive
def test_TCR22_optional_company_and_address2_succeeds(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr22"))
    fill_account_info(page, fill_company=True, fill_address2=True)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag="TCR22")


# TC-R23 | Low | Positive
def test_TCR23_title_mrs_selected_succeeds(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr23"))
    fill_account_info(page, title="Mrs")
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag="TCR23")


# TC-R24 | Low | Positive
def test_TCR24_long_address_and_zipcode_accepted(page: Page):
    go_to_signup_form(page)
    submit_signup_form(page, "Ayesha Khan", unique_email("tcr24"))
    fill_account_info(page, address1="123 Test Street " * 10, zipcode="54000541234")
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, screenshot_tag="TCR24")


# TC-R25 | Critical | Positive (end-to-end)
def test_TCR25_continue_shows_logged_in_state(page: Page):
    name = "Ayesha Khan"
    go_to_signup_form(page)
    submit_signup_form(page, name, unique_email("tcr25"))
    fill_account_info(page)
    page.locator("[data-qa=create-account]").click()
    complete_signup_and_logout(page, name, screenshot_tag="TCR25")
