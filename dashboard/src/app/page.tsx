'use client'

import { useState, useEffect } from 'react'
import { Shield, Camera, Activity, BarChart3, Settings, RefreshCw } from 'lucide-react'
import { Device, Detection, DashboardStats } from '@/types'
import { apiClient } from '@/lib/api-client'
import { ConnectionStatus } from '@/components/ConnectionStatus'
import { EnhancedStatsOverview } from '@/components/EnhancedStatsOverview'
import { EnhancedDeviceCard } from '@/components/EnhancedDeviceCard'
import { EnhancedDetectionList } from '@/components/EnhancedDetectionList'
import { ActivityChart } from '@/components/ActivityChart'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export default function Dashboard() {
  const [devices, setDevices] = useState<Device[]>([])
  const [detections, setDetections] = useState<Detection[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true)
    
    try {
      const [devicesData, detectionsData, statsData] = await Promise.all([
        apiClient.get<{ devices: Device[] }>('/api/devices'),
        apiClient.get<{ detections: Detection[] }>('/api/detections?limit=50'),
        apiClient.get<DashboardStats>('/api/stats')
      ])

      setDevices(devicesData.devices || [])
      setDetections(detectionsData.detections || [])
      setStats(statsData)
      setError(null)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Dashboard fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    fetchDashboardData(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="relative mb-6">
            <Shield className="w-20 h-20 text-green-500 mx-auto" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 border-4 border-green-500/30 border-t-green-500 rounded-full animate-spin" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">OPTIC-SHIELD</h2>
          <LoadingSpinner label="Initializing Dashboard..." size="sm" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/80 backdrop-blur-xl border-r border-slate-700/50 shadow-lg flex flex-col">
        <div className="p-6 border-b border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Shield className="w-8 h-8 text-green-500" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                OPTIC-SHIELD
              </h1>
              <p className="text-xs text-slate-400">Wildlife Detection</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            icon={<BarChart3 className="w-4 h-4" />}
          >
            Dashboard
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            icon={<Camera className="w-4 h-4" />}
          >
            Devices
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            icon={<Activity className="w-4 h-4" />}
          >
            Detections
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            icon={<Settings className="w-4 h-4" />}
          >
            Settings
          </Button>
        </nav>
        
        <div className="p-4 border-t border-slate-700/50 space-y-2">
          <ConnectionStatus />
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            loading={refreshing}
            icon={<RefreshCw className="w-4 h-4" />}
            className="w-full"
          >
            Refresh
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">
        {error && (
          <Alert variant="error" title="Connection Error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <EnhancedStatsOverview stats={stats} />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-1 space-y-6">
            <Card gradient>
              <CardHeader>
                <CardTitle 
                  icon={<Camera className="w-5 h-5" />}
                  badge={
                    <Badge variant="info" size="sm">
                      {devices.length} total
                    </Badge>
                  }
                >
                  Connected Devices
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 max-h-[800px] overflow-y-auto custom-scrollbar">
                {devices.length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <Camera className="w-16 h-16 mx-auto mb-4 opacity-20" />
                    <p className="font-medium mb-1">No devices registered</p>
                    <p className="text-sm">Devices will appear here when connected</p>
                  </div>
                ) : (
                  devices.map(device => (
                    <EnhancedDeviceCard key={device.id} device={device} />
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          <div className="xl:col-span-2 space-y-6">
            <Card gradient>
              <CardHeader>
                <CardTitle 
                  icon={<BarChart3 className="w-5 h-5" />}
                  badge={
                    lastUpdate && (
                      <span className="text-xs text-slate-500">
                        Updated {lastUpdate.toLocaleTimeString()}
                      </span>
                    )
                  }
                >
                  Activity Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityChart stats={stats} />
              </CardContent>
            </Card>

            <Card gradient>
              <CardHeader>
                <CardTitle 
                  icon={<Activity className="w-5 h-5" />}
                  badge={
                    <Badge variant="success" size="sm">
                      {detections.length} recent
                    </Badge>
                  }
                >
                  Recent Detections
                </CardTitle>
              </CardHeader>
              <CardContent>
                <EnhancedDetectionList detections={detections} />
              </CardContent>
            </Card>
          </div>
        </div>
        </div>
      </main>
    </div>
  )
}
