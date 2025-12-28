import { NextRequest, NextResponse } from 'next/server'
import { getDetectionStore } from '@/lib/auth'
import { Detection } from '@/types'

const detectionStore = getDetectionStore()

// Wild cat species filter - ONLY these species are allowed
const WILD_CAT_SPECIES = [
  'tiger',
  'leopard',
  'jaguar',
  'lion',
  'cheetah',
  'snow leopard',
  'clouded leopard',
  'puma',
  'lynx'
]

function isWildCat(className: string): boolean {
  return WILD_CAT_SPECIES.includes(className.toLowerCase())
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get('limit') || '50')
    const deviceId = searchParams.get('device_id')

    let detections: Detection[] = detectionStore.get('all') || []

    // Filter to only include wild cat detections
    detections = detections.filter(d => isWildCat(d.className))

    if (deviceId) {
      detections = detections.filter(d => d.deviceId === deviceId)
    }

    detections = detections.slice(0, limit)

    return NextResponse.json({ 
      success: true, 
      detections,
      count: detections.length
    })
  } catch (error) {
    console.error('Error fetching detections:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch detections' },
      { status: 500 }
    )
  }
}
