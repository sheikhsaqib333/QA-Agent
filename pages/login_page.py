class LoginPage:
    """Everything about the Login screen lives here: what it can find, and what it can do.
    Tests never touch get_by_test_id() directly anymore -- they just call these methods."""

    def __init__(self, page):
        self.page = page  # "self" = "this particular LoginPage, and the browser page it controls"

    def goto(self, url):
        self.page.goto(url)

    def login(self, email, password):
        self.page.get_by_test_id("login-email").fill(email)
        self.page.get_by_test_id("login-password").fill(password)
        self.page.get_by_test_id("login-submit").click()

    def logout(self):
        self.page.get_by_test_id("logout-button").click()

    def switch_to_signup_tab(self):
        self.page.get_by_test_id("tab-signup").click()

    def switch_to_login_tab(self):
        self.page.get_by_test_id("tab-login").click()

    # --- things a test might want to check (assertions) ---
    def email_error(self):
        return self.page.get_by_test_id("login-email-error")

    def password_error(self):
        return self.page.get_by_test_id("login-password-error")

    def banner(self):
        return self.page.get_by_test_id("login-banner")

    def dashboard_welcome(self):
        return self.page.get_by_test_id("dashboard-welcome")

    def email_input(self):
        return self.page.get_by_test_id("login-email")
