# QA Automation Portfolio

![Tests](https://github.com/sheikhsaqib333/QA-Agent/actions/workflows/tests.yml/badge.svg)

Automated test suites built with **Playwright** and **pytest**, covering signup and login flows on a live practice e-commerce site ([automationexercise.com](https://automationexercise.com)), plus a custom-built login/signup practice page with real validation logic.

## What's covered
- 25+ signup test cases (positive, negative, and data-driven across 7 countries)
- 24 login test cases (including security-style checks and full account lifecycle: signup -> login -> delete)
- Page Object Model structure for maintainable test code
- Continuous Integration via GitHub Actions -- every push automatically runs the full suite on a clean machine

## Tech stack
Python, Playwright, pytest, GitHub Actions

## Structure
- `pages/` -- Page Object Model classes
- `test_real_site_signup_full_suite.py` -- signup test suite
- `test_real_site_login_suite.py` -- login test suite
- `login-signup-practice.html` -- custom practice page with real validation logic
- `.github/workflows/tests.yml` -- CI pipeline configuration
