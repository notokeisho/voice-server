import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
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
import { getWhitelist, addToWhitelist, removeFromWhitelist, type WhitelistEntry } from '@/lib/api'

export function WhitelistPage() {
  const [entries, setEntries] = useState<WhitelistEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newGithubId, setNewGithubId] = useState('')
  const [adding, setAdding] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<WhitelistEntry | null>(null)
  const [deleting, setDeleting] = useState(false)

  const fetchWhitelist = async () => {
    try {
      setLoading(true)
      const data = await getWhitelist()
      setEntries(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch whitelist')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWhitelist()
  }, [])

  const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newGithubId.trim()) return

    try {
      setAdding(true)
      await addToWhitelist(newGithubId.trim())
      setNewGithubId('')
      await fetchWhitelist()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add to whitelist')
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    try {
      setDeleting(true)
      await removeFromWhitelist(deleteTarget.id)
      setDeleteTarget(null)
      await fetchWhitelist()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove from whitelist')
    } finally {
      setDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ja-JP')
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
      <h2 className="text-2xl font-bold mb-6">ホワイトリスト管理</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Add new entry */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>ユーザーを追加</CardTitle>
          <CardDescription>
            GitHub ID を入力してホワイトリストに追加します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="flex gap-4">
            <Input
              type="text"
              placeholder="GitHub ID"
              value={newGithubId}
              onChange={(e) => setNewGithubId(e.target.value)}
              className="max-w-xs"
            />
            <Button type="submit" disabled={adding || !newGithubId.trim()}>
              {adding ? '追加中...' : '追加'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Whitelist table */}
      <Card>
        <CardHeader>
          <CardTitle>ホワイトリスト一覧</CardTitle>
          <CardDescription>
            {entries.length} 件のユーザーが登録されています
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>GitHub ID</TableHead>
                <TableHead>登録日時</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {entries.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell className="font-medium">{entry.github_id}</TableCell>
                  <TableCell>{formatDate(entry.created_at)}</TableCell>
                  <TableCell>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => setDeleteTarget(entry)}
                    >
                      削除
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {entries.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-gray-500">
                    ホワイトリストは空です
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>ホワイトリストから削除</DialogTitle>
            <DialogDescription>
              {deleteTarget?.github_id} をホワイトリストから削除しますか？
              このユーザーはサービスを利用できなくなります。
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
