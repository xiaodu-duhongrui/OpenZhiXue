import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AdminUser {
  id: string
  username: string
  realName: string
  role: 'student' | 'parent' | 'teacher' | 'admin'
  email?: string
  phone?: string
  avatar?: string
  status: 'active' | 'inactive' | 'suspended'
  createdAt: string
  updatedAt: string
  classId?: string
  className?: string
}

export interface OperationLog {
  id: string
  adminId: string
  adminName: string
  action: 'create' | 'update' | 'delete' | 'login' | 'logout' | 'import' | 'export'
  targetType: 'user' | 'class' | 'system'
  targetId?: string
  targetName?: string
  detail: string
  ip: string
  createdAt: string
}

export interface DashboardStats {
  studentCount: number
  parentCount: number
  teacherCount: number
  todayNewCount: number
  activeUserCount: number
  totalUserCount: number
}

export interface ImportResult {
  total: number
  success: number
  failed: number
  errors: Array<{ row: number; message: string }>
}

interface UserFilters {
  search: string
  role: string
  status: string
  page: number
  pageSize: number
}

interface LogFilters {
  startDate: string
  endDate: string
  action: string
  targetType: string
  page: number
  pageSize: number
}

interface AdminState {
  userFilters: UserFilters
  logFilters: LogFilters
  setUserFilters: (filters: Partial<UserFilters>) => void
  setLogFilters: (filters: Partial<LogFilters>) => void
  resetUserFilters: () => void
  resetLogFilters: () => void
}

const defaultUserFilters: UserFilters = {
  search: '',
  role: '',
  status: '',
  page: 1,
  pageSize: 10,
}

const defaultLogFilters: LogFilters = {
  startDate: '',
  endDate: '',
  action: '',
  targetType: '',
  page: 1,
  pageSize: 10,
}

export const useAdminStore = create<AdminState>()(
  persist(
    (set) => ({
      userFilters: defaultUserFilters,
      logFilters: defaultLogFilters,
      setUserFilters: (filters) =>
        set((state) => ({
          userFilters: { ...state.userFilters, ...filters },
        })),
      setLogFilters: (filters) =>
        set((state) => ({
          logFilters: { ...state.logFilters, ...filters },
        })),
      resetUserFilters: () => set({ userFilters: defaultUserFilters }),
      resetLogFilters: () => set({ logFilters: defaultLogFilters }),
    }),
    {
      name: 'admin-storage',
      partialize: (state) => ({
        userFilters: state.userFilters,
        logFilters: state.logFilters,
      }),
    }
  )
)
