import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { getUsers, deleteUser, updateUser, getMe, type User } from '@/lib/api'

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [roleChangeTarget, setRoleChangeTarget] = useState<User | null>(null)
  const [changingRole, setChangingRole] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [usersData, meData] = await Promise.all([getUsers(), getMe()])
      setUsers(usersData)
      setCurrentUser(meData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleDelete = async () => {
    if (!deleteTarget) return

    try {
      setDeleting(true)
      await deleteUser(deleteTarget.id)
      setDeleteTarget(null)
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete user')
    } finally {
      setDeleting(false)
    }
  }

  const handleRoleChange = async () => {
    if (!roleChangeTarget) return

    try {
      setChangingRole(true)
      await updateUser(roleChangeTarget.id, !roleChangeTarget.is_admin)
      setRoleChangeTarget(null)
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change role')
    } finally {
      setChangingRole(false)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('ja-JP')
  }

  const getUserDisplayName = (user: User) => {
    return user.github_username || user.github_id
  }

  const isCurrentUser = (user: User) => {
    return currentUser?.id === user.id
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">ユーザー管理</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>登録ユーザー一覧</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>アバター</TableHead>
                <TableHead>ユーザー名</TableHead>
                <TableHead>ロール</TableHead>
                <TableHead>登録日時</TableHead>
                <TableHead>最終ログイン</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    {user.github_avatar ? (
                      <img
                        src={user.github_avatar}
                        alt={getUserDisplayName(user)}
                        className="w-8 h-8 rounded-full"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-200" />
                    )}
                  </TableCell>
                  <TableCell className="font-medium">
                    {getUserDisplayName(user)}
                    {isCurrentUser(user) && (
                      <span className="ml-2 text-xs text-gray-500">(自分)</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {user.is_admin ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        管理者
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        メンバー
                      </span>
                    )}
                  </TableCell>
                  <TableCell>{formatDate(user.created_at)}</TableCell>
                  <TableCell>{formatDate(user.last_login_at)}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant={user.is_admin ? 'outline' : 'default'}
                        size="sm"
                        className="w-32"
                        onClick={() => setRoleChangeTarget(user)}
                        disabled={isCurrentUser(user)}
                      >
                        {user.is_admin ? 'メンバーに変更' : '管理者に変更'}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => setDeleteTarget(user)}
                        disabled={user.is_admin}
                      >
                        削除
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500">
                    ユーザーがいません
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Role Change Confirmation Dialog */}
      <Dialog open={!!roleChangeTarget} onOpenChange={() => setRoleChangeTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>ロールの変更</DialogTitle>
            <DialogDescription>
              {roleChangeTarget && (
                roleChangeTarget.is_admin
                  ? `${getUserDisplayName(roleChangeTarget)} をメンバーに変更しますか？`
                  : `${getUserDisplayName(roleChangeTarget)} を管理者に変更しますか？`
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRoleChangeTarget(null)}>
              キャンセル
            </Button>
            <Button
              onClick={handleRoleChange}
              disabled={changingRole}
            >
              {changingRole ? '変更中...' : '変更'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>ユーザーの削除</DialogTitle>
            <DialogDescription>
              {deleteTarget && getUserDisplayName(deleteTarget)} を削除しますか？この操作は取り消せません。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              キャンセル
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
            >
              {deleting ? '削除中...' : '削除'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
