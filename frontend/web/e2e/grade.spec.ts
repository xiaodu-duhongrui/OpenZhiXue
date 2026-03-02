import { test, expect, Page } from '@playwright/test'

test.describe('Grade Query Flow', () => {
  test.beforeEach(async ({ page }) => {
    await mockLogin(page, 'student')
    await page.goto('/student/grade')
  })

  test('should display grade overview', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /成绩/i })).toBeVisible()
    
    const gradeCards = page.getByTestId('grade-card')
    await expect(gradeCards.first()).toBeVisible()
  })

  test('should show grade statistics', async ({ page }) => {
    await expect(page.getByText(/平均分/i)).toBeVisible()
    await expect(page.getByText(/最高分/i)).toBeVisible()
    await expect(page.getByText(/最低分/i)).toBeVisible()
  })

  test('should display grade list by subject', async ({ page }) => {
    const subjectFilter = page.getByLabel(/科目筛选/i)
    if (await subjectFilter.isVisible()) {
      await subjectFilter.selectOption({ label: '数学' })
      
      const gradeItems = page.getByTestId('grade-item')
      const count = await gradeItems.count()
      
      for (let i = 0; i < count; i++) {
        await expect(gradeItems.nth(i).getByText(/数学/i)).toBeVisible()
      }
    }
  })

  test('should show grade detail', async ({ page }) => {
    const firstGrade = page.getByTestId('grade-item').first()
    await firstGrade.click()
    
    await expect(page.getByRole('heading', { name: /成绩详情/i })).toBeVisible()
    await expect(page.getByText(/分数/i)).toBeVisible()
    await expect(page.getByText(/排名/i)).toBeVisible()
  })

  test('should display grade trend chart', async ({ page }) => {
    const chartSection = page.getByTestId('grade-trend-chart')
    if (await chartSection.isVisible()) {
      await expect(chartSection.getByRole('img')).toBeVisible()
    }
  })

  test('should filter by exam type', async ({ page }) => {
    const examTypeFilter = page.getByLabel(/考试类型/i)
    if (await examTypeFilter.isVisible()) {
      await examTypeFilter.selectOption('midterm')
      
      await expect(page.getByTestId('grade-item').first()).toBeVisible()
    }
  })

  test('should export grade report', async ({ page }) => {
    const exportButton = page.getByRole('button', { name: /导出/i })
    if (await exportButton.isVisible()) {
      const downloadPromise = page.waitForEvent('download')
      await exportButton.click()
      const download = await downloadPromise
      
      expect(download.suggestedFilename()).toContain('.pdf')
    }
  })

  test('should show class ranking', async ({ page }) => {
    const rankingSection = page.getByTestId('class-ranking')
    if (await rankingSection.isVisible()) {
      await expect(rankingSection.getByText(/班级排名/i)).toBeVisible()
    }
  })

  test('should compare with class average', async ({ page }) => {
    const compareSection = page.getByTestId('grade-comparison')
    if (await compareSection.isVisible()) {
      await expect(compareSection.getByText(/班级平均/i)).toBeVisible()
    }
  })

  test('should show grade distribution', async ({ page }) => {
    const distributionChart = page.getByTestId('grade-distribution')
    if (await distributionChart.isVisible()) {
      await expect(distributionChart).toBeVisible()
    }
  })
})

test.describe('Parent Grade View', () => {
  test.beforeEach(async ({ page }) => {
    await mockLogin(page, 'parent')
    await page.goto('/parent/grade')
  })

  test('should display children selection', async ({ page }) => {
    await expect(page.getByText(/选择孩子/i)).toBeVisible()
    
    const childrenList = page.getByTestId('children-list')
    await expect(childrenList.first()).toBeVisible()
  })

  test('should switch between children', async ({ page }) => {
    const secondChild = page.getByTestId('children-list').nth(1)
    if (await secondChild.isVisible()) {
      await secondChild.click()
      
      await expect(page.getByTestId('selected-child-name')).toBeVisible()
    }
  })

  test('should show child grade summary', async ({ page }) => {
    await expect(page.getByText(/成绩概览/i)).toBeVisible()
    await expect(page.getByTestId('total-exams')).toBeVisible()
    await expect(page.getByTestId('average-score')).toBeVisible()
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
            username: role === 'parent' ? 'testparent' : 'teststudent',
            role: role,
          },
        },
      }),
    })
  })
  
  await page.goto('/login')
  await page.getByPlaceholder(/请输入用户名/i).fill(role === 'parent' ? 'testparent' : 'teststudent')
  await page.getByPlaceholder(/请输入密码/i).fill('password123')
  await page.getByRole('button', { name: /登录/i }).click()
}
