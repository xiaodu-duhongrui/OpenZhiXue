import { test, expect, Page } from '@playwright/test'

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await mockLogin(page)
  })

  test('should navigate to student dashboard', async ({ page }) => {
    await page.goto('/student/dashboard')
    
    await expect(page.getByRole('heading', { name: /仪表盘/i })).toBeVisible()
    await expect(page.getByTestId('quick-actions')).toBeVisible()
  })

  test('should display navigation menu', async ({ page }) => {
    await page.goto('/student/dashboard')
    
    const nav = page.getByRole('navigation')
    await expect(nav.getByText(/首页/i)).toBeVisible()
    await expect(nav.getByText(/作业/i)).toBeVisible()
    await expect(nav.getByText(/成绩/i)).toBeVisible()
    await expect(nav.getByText(/课程/i)).toBeVisible()
  })

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/student/dashboard')
    
    await page.getByRole('link', { name: /作业/i }).click()
    await expect(page).toHaveURL(/\/student\/homework/)
    
    await page.getByRole('link', { name: /成绩/i }).click()
    await expect(page).toHaveURL(/\/student\/grade/)
    
    await page.getByRole('link', { name: /课程/i }).click()
    await expect(page).toHaveURL(/\/student\/course/)
  })

  test('should show user profile dropdown', async ({ page }) => {
    await page.goto('/student/dashboard')
    
    await page.getByTestId('user-avatar').click()
    
    const dropdown = page.getByRole('menu')
    await expect(dropdown.getByText(/个人资料/i)).toBeVisible()
    await expect(dropdown.getByText(/设置/i)).toBeVisible()
    await expect(dropdown.getByText(/退出登录/i)).toBeVisible()
  })

  test('should display notifications', async ({ page }) => {
    await page.goto('/student/dashboard')
    
    const notificationBell = page.getByTestId('notification-bell')
    await expect(notificationBell).toBeVisible()
    
    await notificationBell.click()
    
    await expect(page.getByTestId('notification-panel')).toBeVisible()
  })
})

test.describe('Teacher Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await mockLoginAsTeacher(page)
  })

  test('should display teacher dashboard', async ({ page }) => {
    await page.goto('/teacher/dashboard')
    
    await expect(page.getByText(/班级概览/i)).toBeVisible()
    await expect(page.getByTestId('class-stats')).toBeVisible()
  })

  test('should show class management options', async ({ page }) => {
    await page.goto('/teacher/class')
    
    await expect(page.getByText(/班级管理/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /添加班级/i })).toBeVisible()
  })

  test('should display student list', async ({ page }) => {
    await page.goto('/teacher/class/1')
    
    const studentList = page.getByTestId('student-list')
    await expect(studentList.first()).toBeVisible()
  })
})

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await mockLoginAsAdmin(page)
  })

  test('should display admin dashboard', async ({ page }) => {
    await page.goto('/admin/dashboard')
    
    await expect(page.getByText(/系统概览/i)).toBeVisible()
    await expect(page.getByTestId('system-stats')).toBeVisible()
  })

  test('should show user management', async ({ page }) => {
    await page.goto('/admin/users')
    
    await expect(page.getByText(/用户管理/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /添加用户/i })).toBeVisible()
  })

  test('should display operation logs', async ({ page }) => {
    await page.goto('/admin/logs')
    
    await expect(page.getByText(/操作日志/i)).toBeVisible()
    await expect(page.getByTestId('log-table')).toBeVisible()
  })
})

async function mockLogin(page: Page) {
  await page.route('**/api/auth/login', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        code: 0,
        message: 'success',
        data: {
          token: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
          },
          user: {
            id: 1,
            username: 'teststudent',
            role: 'student',
          },
        },
      }),
    })
  })
  
  await page.goto('/login')
  await page.getByPlaceholder(/请输入用户名/i).fill('teststudent')
  await page.getByPlaceholder(/请输入密码/i).fill('password123')
  await page.getByRole('button', { name: /登录/i }).click()
}

async function mockLoginAsTeacher(page: Page) {
  await page.route('**/api/auth/login', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        code: 0,
        message: 'success',
        data: {
          token: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
          },
          user: {
            id: 2,
            username: 'testteacher',
            role: 'teacher',
          },
        },
      }),
    })
  })
  
  await page.goto('/login')
  await page.getByPlaceholder(/请输入用户名/i).fill('testteacher')
  await page.getByPlaceholder(/请输入密码/i).fill('password123')
  await page.getByRole('button', { name: /登录/i }).click()
}

async function mockLoginAsAdmin(page: Page) {
  await page.route('**/api/auth/login', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        code: 0,
        message: 'success',
        data: {
          token: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
          },
          user: {
            id: 0,
            username: 'admin',
            role: 'admin',
          },
        },
      }),
    })
  })
  
  await page.goto('/login')
  await page.getByPlaceholder(/请输入用户名/i).fill('admin')
  await page.getByPlaceholder(/请输入密码/i).fill('admin123')
  await page.getByRole('button', { name: /登录/i }).click()
}
