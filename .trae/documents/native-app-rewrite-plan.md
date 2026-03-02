# 学生端移动应用原生重写计划

## 一、项目概述

### 目标
将现有的 Flutter 学生端移动应用重写为原生应用：
- **Android**: 使用 Java/Kotlin 开发
- **iOS**: 使用 Swift 开发

### 重写原因
1. 原生性能更优，启动速度更快
2. 更好的平台特性集成
3. 更小的应用体积
4. 更流畅的用户体验

### 现有功能模块
| 模块 | 功能点 |
|------|--------|
| 首页仪表盘 | 欢迎卡片、快捷入口、最近作业、下拉刷新 |
| 作业管理 | 列表筛选、详情查看、作业提交、批改结果 |
| 成绩查询 | 成绩列表、详情、排名、趋势分析 |
| 课程学习 | 课程列表、详情、课时列表 |
| 课程表 | 周视图、周次切换、今日高亮 |
| 消息通知 | 消息列表、分类筛选、已读标记、推送 |
| 个人中心 | 个人信息、设置、主题切换 |
| 错题本 | 错题收集、分类、重做、导出 |
| 试卷原卷 | 答题卡查看、批阅痕迹 |
| 学情分析 | 雷达图、趋势图、学习建议 |

---

## 二、Android 原生应用 (Java/Kotlin)

### 项目结构
```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/openzhixue/student/
│   │   │   │   ├── OpenZhixueApp.kt
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── ApiClient.kt
│   │   │   │   │   │   ├── AuthApi.kt
│   │   │   │   │   │   ├── HomeworkApi.kt
│   │   │   │   │   │   ├── GradeApi.kt
│   │   │   │   │   │   ├── CourseApi.kt
│   │   │   │   │   │   └── NotificationApi.kt
│   │   │   │   │   ├── model/
│   │   │   │   │   │   ├── User.kt
│   │   │   │   │   │   ├── Homework.kt
│   │   │   │   │   │   ├── Grade.kt
│   │   │   │   │   │   ├── Course.kt
│   │   │   │   │   │   ├── Notification.kt
│   │   │   │   │   │   ├── Mistake.kt
│   │   │   │   │   │   ├── ExamPaper.kt
│   │   │   │   │   │   └── Analytics.kt
│   │   │   │   │   ├── repository/
│   │   │   │   │   │   ├── UserRepository.kt
│   │   │   │   │   │   ├── HomeworkRepository.kt
│   │   │   │   │   │   └── GradeRepository.kt
│   │   │   │   │   └── local/
│   │   │   │   │       ├── SharedPreferencesManager.kt
│   │   │   │   │       └── CacheManager.kt
│   │   │   │   ├── ui/
│   │   │   │   │   ├── theme/
│   │   │   │   │   │   ├── Color.kt
│   │   │   │   │   │   ├── Theme.kt
│   │   │   │   │   │   └── Typography.kt
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── CardView.kt
│   │   │   │   │   │   ├── ListItemView.kt
│   │   │   │   │   │   ├── LoadingView.kt
│   │   │   │   │   │   ├── EmptyStateView.kt
│   │   │   │   │   │   └── ErrorStateView.kt
│   │   │   │   │   ├── screens/
│   │   │   │   │   │   ├── home/
│   │   │   │   │   │   │   ├── HomeScreen.kt
│   │   │   │   │   │   │   └── HomeViewModel.kt
│   │   │   │   │   │   ├── homework/
│   │   │   │   │   │   │   ├── HomeworkListScreen.kt
│   │   │   │   │   │   │   ├── HomeworkDetailScreen.kt
│   │   │   │   │   │   │   └── HomeworkViewModel.kt
│   │   │   │   │   │   ├── grades/
│   │   │   │   │   │   │   ├── GradeListScreen.kt
│   │   │   │   │   │   │   ├── GradeDetailScreen.kt
│   │   │   │   │   │   │   └── GradeViewModel.kt
│   │   │   │   │   │   ├── courses/
│   │   │   │   │   │   │   ├── CourseListScreen.kt
│   │   │   │   │   │   │   ├── ScheduleScreen.kt
│   │   │   │   │   │   │   └── CourseViewModel.kt
│   │   │   │   │   │   ├── mistakes/
│   │   │   │   │   │   │   ├── MistakeListScreen.kt
│   │   │   │   │   │   │   ├── MistakeDetailScreen.kt
│   │   │   │   │   │   │   └── MistakeViewModel.kt
│   │   │   │   │   │   ├── analytics/
│   │   │   │   │   │   │   ├── AnalyticsScreen.kt
│   │   │   │   │   │   │   └── AnalyticsViewModel.kt
│   │   │   │   │   │   ├── notification/
│   │   │   │   │   │   │   ├── NotificationListScreen.kt
│   │   │   │   │   │   │   └── NotificationViewModel.kt
│   │   │   │   │   │   └── profile/
│   │   │   │   │   │       ├── ProfileScreen.kt
│   │   │   │   │   │       ├── SettingsScreen.kt
│   │   │   │   │   │       └── ProfileViewModel.kt
│   │   │   │   │   └── navigation/
│   │   │   │   │       ├── NavGraph.kt
│   │   │   │   │       └── BottomNavBar.kt
│   │   │   │   └── util/
│   │   │   │       ├── DateUtils.kt
│   │   │   │       ├── StringUtils.kt
│   │   │   │       └── ImageUtils.kt
│   │   │   ├── res/
│   │   │   │   ├── drawable/
│   │   │   │   ├── layout/
│   │   │   │   ├── values/
│   │   │   │   │   ├── colors.xml
│   │   │   │   │   ├── strings.xml
│   │   │   │   │   └── styles.xml
│   │   │   │   └── mipmap/
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

### 技术栈
- **语言**: Kotlin
- **最低 SDK**: Android 6.0 (API 23)
- **架构**: MVVM + Repository Pattern
- **依赖库**:
  - Retrofit2 (网络请求)
  - OkHttp3 (网络层)
  - Gson (JSON 解析)
  - Glide (图片加载)
  - Room (本地数据库)
  - DataStore (偏好存储)
  - MPAndroidChart (图表)
  - PhotoView (图片查看)
  - Coroutines (异步)
  - Lifecycle/LiveData/ViewModel
  - Navigation Component
  - Material Design Components

### 实现任务

#### Phase 1: 项目初始化
- [ ] Task A1: 创建 Android 项目结构
- [ ] Task A2: 配置 Gradle 依赖
- [ ] Task A3: 创建基础架构类
- [ ] Task A4: 实现网络请求层
- [ ] Task A5: 实现本地存储层

#### Phase 2: 核心功能实现
- [ ] Task A6: 实现登录认证模块
- [ ] Task A7: 实现首页仪表盘
- [ ] Task A8: 实现作业管理模块
- [ ] Task A9: 实现成绩查询模块
- [ ] Task A10: 实现课程学习模块

#### Phase 3: 高级功能实现
- [ ] Task A11: 实现课程表周视图
- [ ] Task A12: 实现消息通知模块
- [ ] Task A13: 实现错题本模块
- [ ] Task A14: 实现试卷原卷模块
- [ ] Task A15: 实现学情分析模块

#### Phase 4: 完善和测试
- [ ] Task A16: 实现个人中心模块
- [ ] Task A17: 实现主题切换功能
- [ ] Task A18: 性能优化
- [ ] Task A19: 单元测试
- [ ] Task A20: 集成测试

---

## 三、iOS 原生应用 (Swift)

### 项目结构
```
ios/
├── OpenZhixueStudent/
│   ├── App/
│   │   ├── OpenZhixueApp.swift
│   │   ├── AppDelegate.swift
│   │   └── SceneDelegate.swift
│   ├── Data/
│   │   ├── API/
│   │   │   ├── APIClient.swift
│   │   │   ├── AuthAPI.swift
│   │   │   ├── HomeworkAPI.swift
│   │   │   ├── GradeAPI.swift
│   │   │   ├── CourseAPI.swift
│   │   │   └── NotificationAPI.swift
│   │   ├── Models/
│   │   │   ├── User.swift
│   │   │   ├── Homework.swift
│   │   │   ├── Grade.swift
│   │   │   ├── Course.swift
│   │   │   ├── Notification.swift
│   │   │   ├── Mistake.swift
│   │   │   ├── ExamPaper.swift
│   │   │   └── Analytics.swift
│   │   ├── Repositories/
│   │   │   ├── UserRepository.swift
│   │   │   ├── HomeworkRepository.swift
│   │   │   └── GradeRepository.swift
│   │   └── Local/
│   │       ├── UserDefaultsManager.swift
│   │       ├── KeychainManager.swift
│   │       └── CacheManager.swift
│   ├── UI/
│   │   ├── Theme/
│   │   │   ├── Colors.swift
│   │   │   ├── Typography.swift
│   │   │   └── AppTheme.swift
│   │   ├── Components/
│   │   │   ├── CardView.swift
│   │   │   ├── ListItemView.swift
│   │   │   ├── LoadingView.swift
│   │   │   ├── EmptyStateView.swift
│   │   │   └── ErrorStateView.swift
│   │   ├── Screens/
│   │   │   ├── Home/
│   │   │   │   ├── HomeView.swift
│   │   │   │   └── HomeViewModel.swift
│   │   │   ├── Homework/
│   │   │   │   ├── HomeworkListView.swift
│   │   │   │   ├── HomeworkDetailView.swift
│   │   │   │   └── HomeworkViewModel.swift
│   │   │   ├── Grades/
│   │   │   │   ├── GradeListView.swift
│   │   │   │   ├── GradeDetailView.swift
│   │   │   │   └── GradeViewModel.swift
│   │   │   ├── Courses/
│   │   │   │   ├── CourseListView.swift
│   │   │   │   ├── ScheduleView.swift
│   │   │   │   └── CourseViewModel.swift
│   │   │   ├── Mistakes/
│   │   │   │   ├── MistakeListView.swift
│   │   │   │   ├── MistakeDetailView.swift
│   │   │   │   └── MistakeViewModel.swift
│   │   │   ├── Analytics/
│   │   │   │   ├── AnalyticsView.swift
│   │   │   │   └── AnalyticsViewModel.swift
│   │   │   ├── Notification/
│   │   │   │   ├── NotificationListView.swift
│   │   │   │   └── NotificationViewModel.swift
│   │   │   └── Profile/
│   │   │       ├── ProfileView.swift
│   │   │       ├── SettingsView.swift
│   │   │       └── ProfileViewModel.swift
│   │   ├── Navigation/
│   │   │   ├── NavigationRouter.swift
│   │   │   └── TabBarView.swift
│   │   └── Utils/
│   │       ├── DateUtils.swift
│   │       ├── StringUtils.swift
│   │       └── ImageUtils.swift
│   ├── Resources/
│   │   ├── Assets.xcassets/
│   │   └── LaunchScreen.storyboard
│   ├── Info.plist
│   └── Entitlements.plist
├── OpenZhixueStudent.xcodeproj
├── OpenZhixueStudentTests/
└── Podfile
```

### 技术栈
- **语言**: Swift 5.9+
- **最低版本**: iOS 13.0
- **架构**: MVVM + Repository Pattern
- **依赖库**:
  - Alamofire (网络请求)
  - Kingfisher (图片加载)
  - SQLite.swift (本地数据库)
  - Charts (图表)
  - SDWebImage (图片缓存)
  - Combine (响应式)
  - SwiftUI
  - UIKit

### 实现任务

#### Phase 1: 项目初始化
- [ ] Task I1: 创建 iOS 项目结构
- [ ] Task I2: 配置 CocoaPods 依赖
- [ ] Task I3: 创建基础架构类
- [ ] Task I4: 实现网络请求层
- [ ] Task I5: 实现本地存储层

#### Phase 2: 核心功能实现
- [ ] Task I6: 实现登录认证模块
- [ ] Task I7: 实现首页仪表盘
- [ ] Task I8: 实现作业管理模块
- [ ] Task I9: 实现成绩查询模块
- [ ] Task I10: 实现课程学习模块

#### Phase 3: 高级功能实现
- [ ] Task I11: 实现课程表周视图
- [ ] Task I12: 实现消息通知模块
- [ ] Task I13: 实现错题本模块
- [ ] Task I14: 实现试卷原卷模块
- [ ] Task I15: 实现学情分析模块

#### Phase 4: 完善和测试
- [ ] Task I16: 实现个人中心模块
- [ ] Task I17: 实现主题切换功能
- [ ] Task I18: 性能优化
- [ ] Task I19: 单元测试
- [ ] Task I20: UI测试

---

## 四、共享模块

### API 接口定义
两个平台共享相同的 API 接口规范：

```
基础URL: https://api.openzhixue.com/v1

认证接口:
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh

作业接口:
- GET /homework
- GET /homework/:id
- POST /homework/:id/submit

成绩接口:
- GET /grades
- GET /grades/:id
- GET /grades/trends
- GET /grades/analysis

课程接口:
- GET /courses
- GET /courses/:id
- GET /courses/schedule

错题接口:
- GET /mistakes
- GET /mistakes/:id
- POST /mistakes/:id/practice

通知接口:
- GET /notifications
- GET /notifications/:id
- POST /notifications/:id/read
```

### 数据模型
两个平台使用相同的数据模型结构，仅语言实现不同。

---

## 五、时间估算

| 阶段 | Android | iOS | 说明 |
|------|---------|-----|------|
| Phase 1 | 3天 | 3天 | 项目初始化 |
| Phase 2 | 7天 | 7天 | 核心功能 |
| Phase 3 | 5天 | 5天 | 高级功能 |
| Phase 4 | 3天 | 3天 | 完善测试 |
| **总计** | **18天** | **18天** | 可并行开发 |

---

## 六、验收标准

### 功能验收
- [ ] 所有功能模块正常工作
- [ ] 网络请求正确处理
- [ ] 本地缓存正常工作
- [ ] 推送通知正常接收

### 性能验收
- [ ] 应用启动时间 < 2秒
- [ ] 页面切换流畅
- [ ] 列表滚动无卡顿
- [ ] 内存占用合理

### 兼容性验收
- [ ] Android 6.0+ 正常运行
- [ ] iOS 13.0+ 正常运行
- [ ] 不同屏幕尺寸适配正常

---

## 七、风险和缓解

| 风险 | 缓解措施 |
|------|----------|
| 两个平台功能不一致 | 使用相同的 API 文档和数据模型 |
| 开发周期延长 | 并行开发，共享设计资源 |
| 推送通知配置复杂 | 使用 Firebase/极光推送统一方案 |
| 图表性能问题 | 使用成熟图表库，优化渲染 |
