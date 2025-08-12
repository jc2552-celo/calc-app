import { test, expect } from '@playwright/test';

test('report page shows metrics and recent items', async ({ page }) => {
  // If your app needs auth, do the login flow here first.

  await page.goto('http://localhost:8000/static/report.html');
  await page.waitForSelector('h2:has-text("Metrics")');
  const totalText = await page.locator('#metrics').textContent();
  expect(totalText).toBeTruthy();

  await page.waitForSelector('#recent tbody tr');
  const rows = await page.locator('#recent tbody tr').count();
  expect(rows).toBeGreaterThan(0);
});
