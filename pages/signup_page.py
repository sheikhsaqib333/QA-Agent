class SignupPage:
    """Everything about the Signup screen lives here: what it can find, and what it can do."""

    def __init__(self, page):
        self.page = page

    def goto(self, url):
        self.page.goto(url)
        self.page.get_by_test_id("tab-signup").click()

    def signup(self, name="", email="", password="", confirm="", check_terms=True):
        if name:
            self.page.get_by_test_id("signup-fullname").fill(name)
        if email:
            self.page.get_by_test_id("signup-email").fill(email)
        if password:
            self.page.get_by_test_id("signup-password").fill(password)
        if confirm:
            self.page.get_by_test_id("signup-confirm-password").fill(confirm)
        if check_terms:
            self.page.get_by_test_id("signup-terms").check()
        self.page.get_by_test_id("signup-submit").click()

    def fill_name(self, name):
        self.page.get_by_test_id("signup-fullname").fill(name)

    def submit(self):
        self.page.get_by_test_id("signup-submit").click()

    # --- things a test might want to check (assertions) ---
    def success_banner(self):
        return self.page.get_by_test_id("signup-success")

    def error_banner(self):
        return self.page.get_by_test_id("signup-error-banner")

    def fullname_error(self):
        return self.page.get_by_test_id("signup-fullname-error")

    def email_error(self):
        return self.page.get_by_test_id("signup-email-error")

    def password_error(self):
        return self.page.get_by_test_id("signup-password-error")

    def confirm_password_error(self):
        return self.page.get_by_test_id("signup-confirm-password-error")
