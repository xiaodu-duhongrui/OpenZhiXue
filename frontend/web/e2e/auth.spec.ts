import { test, expect, Page } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should display login page correctly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /欢迎回来/i })).toBeVisible()
    await expect(page.getByPlaceholder(/请输入用户名/i)).toBeVisible()
    await expect(page.getByPlaceholder(/请输入密码/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /登录/i })).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.getByRole('button', { name: /登录/i }).click()
    
    await expect(page.getByText(/请输入用户名/i)).toBeVisible()
    await expect(page.getByText(/请输入密码/i)).toBeVisible()
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByPlaceholder(/请输入用户名/i).fill('invaliduser')
    await page.getByPlaceholder(/请输入密码/i).fill('wrongpassword')
    await page.getByRole('button', { name: /登录/i }).click()
    
    await expect(page.getByText(/用户名或密码错误/i)).toBeVisible()
  })

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.getByPlaceholder(/请输入用户名/i).fill('testuser')
    await page.getByPlaceholder(/请输入密码/i).fill('password123')
    await page.getByRole('button', { name: /登录/i }).click()
    
    await expect(page).toHaveURL(/\/(dashboard|home)/)
    await expect(page.getByText(/testuser/i)).toBeVisible()
  })

  test('should navigate to forgot password page', async ({ page }) => {
    await page.getByText(/忘记密码/i).click()
    
    await expect(page).toHaveURL(/\/forgot-password/)
  })

  test('should navigate to register page', async ({ page }) => {
    await page.getByText(/立即注册/i).click()
    
    await expect(page).toHaveURL(/\/register/)
  })

  test('should remember user session after page reload', async ({ page }) => {
    await page.getByPlaceholder(/请输入用户名/i).fill('testuser')
    await page.getByPlaceholder(/请输入密码/i).fill('password123')
    await page.getByRole('button', { name: /登录/i }).click()
    
    await expect(page).toHaveURL(/\/(dashboard|home)/)
    
    await page.reload()
    
    await expect(page.getByText(/testuser/i)).toBeVisible()
  })

  test('should logout successfully', async ({ page }) => {
    await loginAsUser(page, 'testuser', 'password123')
    
    await page.getByRole('button', { name: /testuser/i }).click()
    await page.getByRole('menuitem', { name: /退出登录/i }).click()
    
    await expect(page).toHaveURL(/\/login/)
  })
})

async function loginAsUser(page: Page, username: string, password: string) {
  await page.goto('/login')
  await page.getByPlaceholder(/请输入用户名/i).fill(username)
  await page.getByPlaceholder(/请输入密码/i).fill(password)
  await page.getByRole('button', { name: /登录/i }).click()
  await expect(page).toHaveURL(/\/(dashboard|home)/)
}
