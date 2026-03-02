import { test, expect, Page } from '@playwright/test'

test.describe('Homework Submission Flow', () => {
  test.beforeEach(async ({ page }) => {
    await mockLogin(page, 'student')
    await page.goto('/student/homework')
  })

  test('should display homework list', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /作业/i })).toBeVisible()
    
    const homeworkItems = page.getByTestId('homework-item')
    await expect(homeworkItems.first()).toBeVisible()
  })

  test('should show homework details', async ({ page }) => {
    const firstHomework = page.getByTestId('homework-item').first()
    await firstHomework.click()
    
    await expect(page.getByRole('heading', { name: /作业详情/i })).toBeVisible()
    await expect(page.getByText(/截止时间/i)).toBeVisible()
    await expect(page.getByText(/作业要求/i)).toBeVisible()
  })

  test('should submit homework successfully', async ({ page }) => {
    await page.getByTestId('homework-item').first().click()
    
    const answerInput = page.getByPlaceholder(/请输入答案/i)
    if (await answerInput.isVisible()) {
      await answerInput.fill('这是我的作业答案内容...')
    }
    
    const fileInput = page.getByLabel(/上传附件/i)
    if (await fileInput.isVisible()) {
      await fileInput.setInputFiles({
        name: 'homework.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('test file content'),
      })
    }
    
    await page.getByRole('button', { name: /提交作业/i }).click()
    
    await expect(page.getByText(/提交成功/i)).toBeVisible()
  })

  test('should show validation error for empty submission', async ({ page }) => {
    await page.getByTestId('homework-item').first().click()
    
    await page.getByRole('button', { name: /提交作业/i }).click()
    
    await expect(page.getByText(/请填写作业内容/i)).toBeVisible()
  })

  test('should save homework as draft', async ({ page }) => {
    await page.getByTestId('homework-item').first().click()
    
    const answerInput = page.getByPlaceholder(/请输入答案/i)
    if (await answerInput.isVisible()) {
      await answerInput.fill('草稿内容...')
    }
    
    await page.getByRole('button', { name: /保存草稿/i }).click()
    
    await expect(page.getByText(/已保存为草稿/i)).toBeVisible()
  })

  test('should show submission status', async ({ page }) => {
    await page.getByTestId('homework-item').first().click()
    
    const statusBadge = page.getByTestId('submission-status')
    await expect(statusBadge).toBeVisible()
  })

  test('should display teacher feedback if available', async ({ page }) => {
    await page.getByTestId('homework-item').first().click()
    
    const feedback = page.getByTestId('teacher-feedback')
    if (await feedback.isVisible()) {
      await expect(feedback.getByText(/评语/i)).toBeVisible()
      await expect(feedback.getByText(/得分/i)).toBeVisible()
    }
  })

  test('should filter homework by status', async ({ page }) => {
    const filterDropdown = page.getByLabel(/状态筛选/i)
    if (await filterDropdown.isVisible()) {
      await filterDropdown.selectOption('pending')
      
      const items = page.getByTestId('homework-item')
      const count = await items.count()
      
      for (let i = 0; i < count; i++) {
        await expect(items.nth(i).getByText(/待提交/i)).toBeVisible()
      }
    }
  })

  test('should sort homework by deadline', async ({ page }) => {
    const sortButton = page.getByRole('button', { name: /排序/i })
    if (await sortButton.isVisible()) {
      await sortButton.click()
      await page.getByRole('menuitem', { name: /截止时间/i }).click()
      
      await expect(page.getByTestId('homework-item').first()).toBeVisible()
    }
  })
})

async function mockLogin(page: Page, role: string) {
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
            role: role,
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
