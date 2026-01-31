import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import {
  getGlobalDictionary,
  addGlobalDictionaryEntry,
  deleteGlobalDictionaryEntry,
  type DictionaryEntry,
} from '@/lib/api'

export function DictionaryPage() {
  const [entries, setEntries] = useState<DictionaryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pattern, setPattern] = useState('')
  const [replacement, setReplacement] = useState('')
  const [adding, setAdding] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<DictionaryEntry | null>(null)
  const [deleting, setDeleting] = useState(false)

  const fetchDictionary = async () => {
    try {
      setLoading(true)
      const data = await getGlobalDictionary()
      setEntries(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dictionary')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDictionary()
  }, [])

  const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!pattern.trim() || !replacement.trim()) return

    try {
      setAdding(true)
      await addGlobalDictionaryEntry(pattern.trim(), replacement.trim())
      setPattern('')
      setReplacement('')
      await fetchDictionary()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add entry')
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    try {
      setDeleting(true)
      await deleteGlobalDictionaryEntry(deleteTarget.id)
      setDeleteTarget(null)
      await fetchDictionary()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete entry')
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
      <h2 className="text-2xl font-bold mb-6">グローバル辞書管理</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Info card */}
      <Card className="mb-6 bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <p className="text-blue-800">
            グローバル辞書は全ユーザーの音声認識結果に適用されます。
            よくある認識ミスや固有名詞の変換ルールを登録してください。
          </p>
        </CardContent>
      </Card>

      {/* Add new entry */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>エントリを追加</CardTitle>
          <CardDescription>
            認識パターンと置換後のテキストを入力してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="pattern">認識パターン</Label>
                <Input
                  id="pattern"
                  type="text"
                  placeholder="例: くろーど"
                  value={pattern}
                  onChange={(e) => setPattern(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="replacement">置換後</Label>
                <Input
                  id="replacement"
                  type="text"
                  placeholder="例: Claude"
                  value={replacement}
                  onChange={(e) => setReplacement(e.target.value)}
                />
              </div>
            </div>
            <Button
              type="submit"
              disabled={adding || !pattern.trim() || !replacement.trim()}
            >
              {adding ? '追加中...' : '追加'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Dictionary table */}
      <Card>
        <CardHeader>
          <CardTitle>辞書エントリ一覧</CardTitle>
          <CardDescription>
            {entries.length} 件のエントリが登録されています
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>認識パターン</TableHead>
                <TableHead>置換後</TableHead>
                <TableHead>登録日時</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {entries.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell className="font-medium">{entry.pattern}</TableCell>
                  <TableCell>{entry.replacement}</TableCell>
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
                  <TableCell colSpan={4} className="text-center text-gray-500">
                    辞書エントリがありません
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
            <DialogTitle>エントリの削除</DialogTitle>
            <DialogDescription>
              「{deleteTarget?.pattern}」→「{deleteTarget?.replacement}」を削除しますか？
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
