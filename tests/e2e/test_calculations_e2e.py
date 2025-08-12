# tests/e2e/test_calculations_e2e.py
from playwright.sync_api import Page

BASE = "http://127.0.0.1:8001"  # server already running in Terminal 1

def test_bread_flow(page: Page, tmp_path):
    page.set_default_timeout(20000)

    # Start at "/" -> should redirect to /login
    page.goto(f"{BASE}/", wait_until="domcontentloaded")
    page.wait_for_url("**/login")

    # Login
    page.fill("input[name=username]", "e2e_user")
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/")
    page.wait_for_selector("text=Calculations")

    # Add
    page.select_option("select[name=operation]", "add")
    page.fill("input[name=a]", "7")
    page.fill("input[name=b]", "8")
    page.click("form button[type=submit]")
    row = page.locator("tbody#calc-body tr").first
    row.wait_for()
    assert "15" in row.text_content()

    # Edit
    row.locator("button:has-text('Edit')").click()
    row.locator("select[name=operation]").select_option("multiply")
    row.locator("input[name=a]").fill("3")
    row.locator("input[name=b]").fill("5")
    row.locator("form button[type=submit]").click()

    # DOM is replaced; reselect the first row
    row = page.locator("tbody#calc-body tr").first
    row.wait_for()
    page.wait_for_selector("tbody#calc-body tr:first-child :text('15')")

    # Delete
    before = page.locator("tbody#calc-body tr").count()
    row.locator("button:has-text('Delete')").click()
    page.wait_for_timeout(300)
    after = page.locator("tbody#calc-body tr").count()
    assert after <= before
