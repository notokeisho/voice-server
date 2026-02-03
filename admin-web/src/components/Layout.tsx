import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { removeToken, type User } from '@/lib/api'
import { cn } from '@/lib/utils'
import { LanguageSwitcher } from '@/lib/i18n'
import { LayoutDashboard, Users, UserCheck, BookOpen, type LucideIcon } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  user: User | null
}

interface NavItem {
  path: string
  label: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  { path: '/', label: 'ダッシュボード', icon: LayoutDashboard },
  { path: '/users', label: 'ユーザー管理', icon: Users },
  { path: '/whitelist', label: 'ホワイトリスト', icon: UserCheck },
  { path: '/dictionary', label: 'グローバル辞書', icon: BookOpen },
]

export function Layout({ children, user }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold text-gray-900">
              VoiceServer Admin
            </h1>
            <div className="flex items-center gap-4">
              {user && (
                <>
                  <div className="flex items-center gap-2">
                    {user.github_avatar && (
                      <img
                        src={user.github_avatar}
                        alt={user.github_id}
                        className="w-8 h-8 rounded-full"
                      />
                    )}
                    <span className="text-sm text-gray-700">{user.github_id}</span>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleLogout}>
                    ログアウト
                  </Button>
                </>
              )}
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 min-h-[calc(100vh-4rem)] bg-white shadow-sm">
          <ul className="py-4">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={cn(
                    'flex items-center gap-3 px-6 py-3 text-gray-700 hover:bg-gray-50',
                    location.pathname === item.path && 'bg-gray-100 font-medium'
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Main content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
