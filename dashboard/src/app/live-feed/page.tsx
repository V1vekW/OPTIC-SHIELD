'use client'

import { useState, useEffect } from 'react'
import { Detection } from '@/types'
import { apiClient } from '@/lib/api-client'
import { EnhancedDetectionList } from '@/components/EnhancedDetectionList'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Alert } from '@/components/ui/Alert'
import { Sidebar } from '@/components/layout/Sidebar'
import { Zap, Wifi } from 'lucide-react'

export default function LiveFeedPage() {
    const [detections, setDetections] = useState<Detection[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [refreshing, setRefreshing] = useState(false)
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

    // Dummy connection status for now - ideal would be to use useDeviceStream but simplicity first
    const isStreamConnected = true

    useEffect(() => {
        fetchDetections()
        const interval = setInterval(() => fetchDetections(), 5000) // Polling every 5s for live feed
        return () => clearInterval(interval)
    }, [])

    const fetchDetections = async (showRefreshing = false) => {
        if (showRefreshing) setRefreshing(true)

        try {
            const { detections } = await apiClient.get<{ detections: Detection[] }>('/api/detections?limit=50')
            setDetections(detections || [])
            setError(null)
            setLastUpdate(new Date())
        } catch (err) {
            console.error('Live feed fetch error:', err)
            setError(err instanceof Error ? err.message : 'Failed to fetch detections')
        } finally {
            setLoading(false)
            setRefreshing(false)
        }
    }

    const handleRefresh = () => {
        fetchDetections(true)
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <LoadingSpinner label="Loading Live Feed..." size="lg" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background text-slate-100 flex font-sans">
            <Sidebar onRefresh={handleRefresh} isRefreshing={refreshing} />

            <main className="flex-1 overflow-auto relative p-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight mb-1 flex items-center gap-3">
                            <Zap className="w-8 h-8 text-nexus-accent" />
                            Live Detection Feed
                        </h1>
                        <p className="text-slate-400">Real-time monitoring of all connected devices</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium transition-all ${isStreamConnected
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                                : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                            }`}>
                            <Wifi className="w-3 h-3" />
                            <span>{isStreamConnected ? 'Live Stream Active' : 'Connecting...'}</span>
                        </div>
                    </div>
                </div>

                {error && (
                    <Alert variant="error" title="Feed Error" onClose={() => setError(null)} className="mb-6">
                        {error}
                    </Alert>
                )}

                <div className="glass-panel p-1 rounded-2xl overflow-hidden shadow-2xl shadow-black/50 border-white/5">
                    <EnhancedDetectionList detections={detections} />
                </div>
            </main>
        </div>
    )
}
