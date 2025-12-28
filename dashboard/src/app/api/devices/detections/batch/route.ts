import { NextRequest, NextResponse } from 'next/server'
import { verifyRequest, getDeviceStore, getDetectionStore } from '@/lib/auth'
import { Detection } from '@/types'

const deviceStore = getDeviceStore()
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

export async function POST(request: NextRequest) {
  try {
    const authResult = verifyRequest(request)
    if (!authResult.valid) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { device_id, detections: incomingDetections } = body

    if (!device_id || !Array.isArray(incomingDetections)) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    const device = deviceStore.get(device_id)
    const deviceName = device?.name || device_id

    const storedDetections = detectionStore.get('all') || []
    let addedCount = 0
    let rejectedCount = 0

    for (const det of incomingDetections) {
      // Filter out non-wild-cat species
      if (!isWildCat(det.class_name)) {
        rejectedCount++
        continue
      }

      const detection: Detection = {
        id: det.detection_id || Date.now() + addedCount,
        deviceId: device_id,
        deviceName: deviceName,
        timestamp: new Date(det.timestamp * 1000).toISOString(),
        className: det.class_name,
        confidence: det.confidence,
        bbox: det.bbox || [],
        imageUrl: det.image_base64 ? `data:image/jpeg;base64,${det.image_base64}` : undefined
      }

      storedDetections.unshift(detection)
      addedCount++
    }

    if (storedDetections.length > 1000) {
      storedDetections.splice(1000)
    }
    detectionStore.set('all', storedDetections)

    if (device) {
      device.stats.detectionCount = (device.stats.detectionCount || 0) + addedCount
      device.lastSeen = new Date().toISOString()
      deviceStore.set(device_id, device)
    }

    console.log(`Batch: ${addedCount} wild cat detections received from ${deviceName}${rejectedCount > 0 ? ` (${rejectedCount} non-wild-cat detections rejected)` : ''}`)

    return NextResponse.json({ 
      success: true, 
      message: `${addedCount} detections recorded`,
      count: addedCount
    })
  } catch (error) {
    console.error('Error recording batch detections:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to record detections' },
      { status: 500 }
    )
  }
}
