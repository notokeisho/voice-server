import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { getStatus, type StatusResponse } from '@/lib/api'

export function DashboardPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await getStatus()
        setStatus(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
      case 'connected':
        return 'text-green-600 bg-green-100'
      case 'error':
      case 'disconnected':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-600 py-8">
        <p>エラー: {error}</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">ダッシュボード</h2>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>サーバー状態</CardTitle>
            <CardDescription>メインサーバー</CardDescription>
          </CardHeader>
          <CardContent>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status?.status || '')}`}>
              {status?.status === 'ok' ? '正常' : status?.status}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Whisper サーバー</CardTitle>
            <CardDescription>音声認識エンジン</CardDescription>
          </CardHeader>
          <CardContent>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status?.whisper_server || '')}`}>
              {status?.whisper_server === 'connected' ? '接続済み' : status?.whisper_server}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>データベース</CardTitle>
            <CardDescription>PostgreSQL</CardDescription>
          </CardHeader>
          <CardContent>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status?.database || '')}`}>
              {status?.database === 'connected' ? '接続済み' : status?.database}
            </span>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
