#!/usr/bin/env python3
"""
Device Simulator for OPTIC-SHIELD
Simulates multiple wildlife detection devices sending telemetry to the dashboard.
Useful for testing the portal connectivity system.
"""

import os
import sys
import time
import json
import random
import argparse
import threading
import urllib.request
import urllib.error
import base64
import hashlib
import hmac
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Wildlife locations for simulation - Maharashtra Pune villages
WILDLIFE_LOCATIONS = [
    {
        "name": "Lonavala Forest Reserve",
        "latitude": 18.7540,
        "longitude": 73.4057,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Khandala Wildlife Zone",
        "latitude": 18.7512,
        "longitude": 73.3765,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Mulshi Lake Area",
        "latitude": 18.6417,
        "longitude": 73.5178,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Pawna Dam Region",
        "latitude": 18.6989,
        "longitude": 73.5113,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Tikona Fort Forest",
        "latitude": 18.6320,
        "longitude": 73.5340,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Lavasa Hills",
        "latitude": 18.4135,
        "longitude": 73.5174,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Rajgad Fort Area",
        "latitude": 18.2475,
        "longitude": 73.6525,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Torna Fort Region",
        "latitude": 18.2806,
        "longitude": 73.7197,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Sinhagad Wildlife",
        "latitude": 18.3589,
        "longitude": 73.7547,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Panshet Dam Forest",
        "latitude": 18.4167,
        "longitude": 73.4167,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Varasgaon Wildlife",
        "latitude": 18.4333,
        "longitude": 73.7333,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Bhimashankar Reserve",
        "latitude": 19.0778,
        "longitude": 73.5325,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Matheran Eco Zone",
        "latitude": 18.9833,
        "longitude": 73.2667,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Karnala Bird Sanctuary",
        "latitude": 18.8750,
        "longitude": 73.1167,
        "timezone": "Asia/Kolkata",
    },
    {
        "name": "Sanjay Gandhi National Park",
        "latitude": 19.2147,
        "longitude": 72.9315,
        "timezone": "Asia/Kolkata",
    },
]

CAMERA_MODELS = [
    "Pi Camera Module 3",
    "Pi Camera Module 3 Wide",
    "Pi Camera HQ",
    "Arducam 16MP",
    "USB Webcam HD",
    "Night Vision IR Camera",
]

HARDWARE_MODELS = [
    "Raspberry Pi 5 8GB",
    "Raspberry Pi 5 4GB",
    "Raspberry Pi 4 Model B",
    "Jetson Nano",
]

# Wildlife classes for simulation - ONLY wild cats (API only accepts these)
WILDLIFE_CLASSES = {
    "all_cats": [
        {
            "name": "leopard",
            "high_priority": True,
            "confidence_range": (0.7, 0.95),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "tiger",
            "high_priority": True,
            "confidence_range": (0.75, 0.98),
            "images": ["lion.png"],
        },
        {
            "name": "jaguar",
            "high_priority": True,
            "confidence_range": (0.8, 0.96),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "lion",
            "high_priority": True,
            "confidence_range": (0.75, 0.97),
            "images": ["lion.png"],
        },
        {
            "name": "cheetah",
            "high_priority": True,
            "confidence_range": (0.7, 0.92),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "snow leopard",
            "high_priority": True,
            "confidence_range": (0.65, 0.90),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "clouded leopard",
            "high_priority": True,
            "confidence_range": (0.6, 0.88),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "puma",
            "high_priority": True,
            "confidence_range": (0.7, 0.93),
            "images": ["lion.png"],
        },
        {
            "name": "lynx",
            "high_priority": True,
            "confidence_range": (0.65, 0.90),
            "images": ["jaguar.jpg"],
        },
    ],
    "leopard": [
        {
            "name": "leopard",
            "high_priority": True,
            "confidence_range": (0.75, 0.98),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "snow leopard",
            "high_priority": True,
            "confidence_range": (0.70, 0.95),
            "images": ["jaguar.jpg"],
        },
        {
            "name": "clouded leopard",
            "high_priority": True,
            "confidence_range": (0.68, 0.92),
            "images": ["jaguar.jpg"],
        },
    ],
}

# Demo images for simulation (both are leopard-like big cats)
DEMO_IMAGES = ["jaguar.jpg", "lion.png"]

# Animal categories available
ANIMAL_CATEGORIES = list(WILDLIFE_CLASSES.keys())


@dataclass
class SimulatedDevice:
    """Represents a simulated wildlife detection device."""

    device_id: str
    name: str
    location: Dict[str, Any]
    hardware_model: str
    cameras: List[Dict[str, Any]]
    start_time: float

    # Simulated metrics
    cpu_base: float = 20.0
    memory_base: float = 40.0
    temperature_base: float = 45.0
    storage_used: float = 10.0
    storage_total: float = 64.0
    power_source: str = "ac"
    detection_count: int = 0


class DeviceSimulator:
    """Simulates multiple devices sending telemetry to the dashboard."""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        device_secret: str = "",
        num_devices: int = 3,
        heartbeat_interval: int = 10,
        detection_probability: float = 0.1,
        send_images: bool = True,
        animal_category: str = "leopard",
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.device_secret = device_secret
        self.num_devices = num_devices
        self.heartbeat_interval = heartbeat_interval
        self.detection_probability = detection_probability
        self.send_images = send_images
        self.animal_category = animal_category

        # Get wildlife classes for the selected category
        self.wildlife_classes = WILDLIFE_CLASSES.get(
            animal_category, WILDLIFE_CLASSES["leopard"]
        )

        self.devices: List[SimulatedDevice] = []
        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []
        self._demo_images: Dict[str, str] = {}

    def _generate_device_id(self) -> str:
        """Generate a unique device ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    def _create_cameras(self, device_id: str, count: int = 1) -> List[Dict[str, Any]]:
        """Create simulated camera configurations."""
        cameras = []
        for i in range(count):
            cameras.append(
                {
                    "id": f"cam-{device_id}-{i}",
                    "name": f"Camera {i + 1}",
                    "model": random.choice(CAMERA_MODELS),
                    "resolution": random.choice(["640x480", "1280x720", "1920x1080"]),
                    "status": "active",
                }
            )
        return cameras

    def _create_device(self, index: int) -> SimulatedDevice:
        """Create a simulated device."""
        device_id = self._generate_device_id()
        location = WILDLIFE_LOCATIONS[index % len(WILDLIFE_LOCATIONS)]

        return SimulatedDevice(
            device_id=device_id,
            name=f"OPTIC-{device_id.upper()}",
            location=location,
            hardware_model=random.choice(HARDWARE_MODELS),
            cameras=self._create_cameras(device_id, random.randint(1, 3)),
            start_time=time.time(),
            cpu_base=random.uniform(15, 35),
            memory_base=random.uniform(30, 50),
            temperature_base=random.uniform(40, 55),
            storage_used=random.uniform(5, 30),
            storage_total=random.choice([32, 64, 128, 256]),
            power_source=random.choice(["ac", "solar", "battery"]),
        )

    def _load_demo_images(self):
        """Load demo images for detection simulation."""
        demo_dir = Path(__file__).parent.parent / "demo-img"

        for image_name in DEMO_IMAGES:
            image_path = demo_dir / image_name
            if image_path.exists():
                try:
                    with open(image_path, "rb") as f:
                        image_data = f.read()
                        # Compress image if needed (simple resize simulation)
                        if len(image_data) > 500 * 1024:  # If > 500KB
                            # For simulation, we'll just note it would be compressed
                            pass
                        self._demo_images[image_name] = base64.b64encode(
                            image_data
                        ).decode()
                        print(
                            f"Loaded demo image: {image_name} ({len(image_data)} bytes)"
                        )
                except Exception as e:
                    print(f"Failed to load {image_name}: {e}")

    def _generate_signature(self, payload: str, timestamp: int, device_id: str) -> str:
        """Generate HMAC signature for secure requests."""
        if not self.device_secret:
            return ""

        message = f"{device_id}:{timestamp}:{payload}"
        signature = hmac.new(
            self.device_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None,
        device_id: str = "",
    ) -> Optional[Dict]:
        """Make an HTTP request to the dashboard API."""
        url = f"{self.api_url}{endpoint}"

        payload = json.dumps(data) if data else ""
        timestamp = int(time.time())

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Device-ID": device_id,
            "X-Timestamp": str(timestamp),
        }

        # Add signature if device secret is provided
        signature = self._generate_signature(payload, timestamp, device_id)
        if signature:
            headers["X-Signature"] = signature

        try:
            req = urllib.request.Request(
                url,
                data=payload.encode() if payload else None,
                headers=headers,
                method=method,
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode()
                return json.loads(response_data) if response_data else {}

        except urllib.error.HTTPError as e:
            print(f"[{device_id}] HTTP error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"[{device_id}] Network error: {e.reason}")
            return None
        except Exception as e:
            print(f"[{device_id}] Request error: {e}")
            return None

    def _simulate_metrics(self, device: SimulatedDevice) -> Dict[str, Any]:
        """Generate simulated telemetry metrics."""
        # Add some variation to base values
        cpu = device.cpu_base + random.uniform(-10, 30)
        cpu = max(5, min(95, cpu))

        memory = device.memory_base + random.uniform(-5, 15)
        memory = max(20, min(90, memory))

        temperature = device.temperature_base + random.uniform(-5, 15)
        temperature = max(35, min(85, temperature))

        # Slowly increase storage over time
        device.storage_used = min(
            device.storage_total * 0.9, device.storage_used + random.uniform(0, 0.1)
        )

        uptime = time.time() - device.start_time

        # Simulate occasional detections
        if random.random() < self.detection_probability:
            device.detection_count += random.randint(1, 3)

        memory_total = random.choice([2048, 4096, 8192])
        memory_used = memory_total * (memory / 100)

        return {
            "uptime_seconds": uptime,
            "detection_count": device.detection_count,
            "system": {
                "cpu_percent": round(cpu, 1),
                "memory_percent": round(memory, 1),
                "memory_used_mb": round(memory_used, 1),
                "memory_total_mb": memory_total,
                "temperature_celsius": round(temperature, 1),
                "disk_percent": round(
                    (device.storage_used / device.storage_total) * 100, 1
                ),
                "disk_used_gb": round(device.storage_used, 2),
                "disk_total_gb": device.storage_total,
            },
            "power": {
                "consumption_watts": round(random.uniform(3, 8), 1),
                "source": device.power_source,
                "battery_percent": (
                    random.randint(60, 100)
                    if device.power_source == "battery"
                    else None
                ),
            },
            "cameras": device.cameras,
            "network": {
                "latency_ms": random.randint(20, 200),
            },
        }

    def _register_device(self, device: SimulatedDevice) -> bool:
        """Register a device with the dashboard."""
        data = {
            "device_id": device.device_id,
            "name": device.name,
            "location": device.location,
            "environment": "production",
            "version": "1.0.0",
            "hardware_model": device.hardware_model,
            "tags": [
                "wildlife",
                "simulation",
                device.location["name"].split()[0].lower(),
            ],
            "cameras": device.cameras,
        }

        response = self._make_request(
            "/api/devices", data=data, device_id=device.device_id
        )

        if response and response.get("success"):
            print(
                f"[{device.device_id}] Registered: {device.name} at {device.location['name']}"
            )
            return True
        return False

    def _send_detection(self, device: SimulatedDevice) -> bool:
        """Send a simulated wildlife detection with image."""
        wildlife = random.choice(self.wildlife_classes)
        camera = random.choice(device.cameras)

        detection_id = int(time.time() * 1000)
        event_id = f"evt-{detection_id}"

        confidence = random.uniform(*wildlife["confidence_range"])
        bbox = [
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(300, 600),
            random.randint(300, 600),
        ]

        data = {
            "event_id": event_id,
            "detection_id": detection_id,
            "device_id": device.device_id,
            "camera_id": camera["id"],
            "timestamp": time.time(),
            "class_name": wildlife["name"],
            "confidence": round(confidence, 3),
            "bbox": bbox,
            "location": {
                "latitude": device.location["latitude"],
                "longitude": device.location["longitude"],
                "name": device.location["name"],
            },
            "metadata": {
                "priority": "high" if wildlife["high_priority"] else "normal",
                "processing_time_ms": random.randint(100, 500),
                "model_version": "yolov8n",
                "camera_name": camera["name"],
                "animal_category": self.animal_category,
            },
        }

        # Select image that matches the wildlife class
        if self.send_images and self._demo_images:
            # Use the image specified for this wildlife class, or fallback to random
            preferred_images = wildlife.get("images", list(self._demo_images.keys()))
            available_images = [
                img for img in preferred_images if img in self._demo_images
            ]
            if available_images:
                image_name = random.choice(available_images)
            else:
                image_name = random.choice(list(self._demo_images.keys()))
            data["image_base64"] = self._demo_images[image_name]

        response = self._make_request(
            "/api/devices/detections", data=data, device_id=device.device_id
        )

        if response and response.get("success"):
            device.detection_count += 1
            priority = "HIGH" if wildlife["high_priority"] else "NORM"
            img_status = "with image" if "image_base64" in data else "no image"
            print(
                f"[{device.device_id}] Detection: {wildlife['name']} ({confidence:.2f}) [{priority}] {img_status}"
            )
            return True
        return False

    def _send_heartbeat(self, device: SimulatedDevice) -> bool:
        """Send a heartbeat for a device."""
        stats = self._simulate_metrics(device)

        data = {
            "device_id": device.device_id,
            "timestamp": time.time(),
            "status": "online",
            "name": device.name,
            "location": device.location,
            "environment": "production",
            "version": "1.0.0",
            "hardware_model": device.hardware_model,
            "tags": [
                "wildlife",
                "simulation",
                device.location["name"].split()[0].lower(),
            ],
            "cameras": device.cameras,
            "stats": stats,
        }

        response = self._make_request(
            "/api/devices/heartbeat", data=data, device_id=device.device_id
        )

        if response and response.get("success"):
            cpu = stats["system"]["cpu_percent"]
            mem = stats["system"]["memory_percent"]
            temp = stats["system"]["temperature_celsius"]
            print(
                f"[{device.device_id}] Heartbeat: CPU={cpu}%, MEM={mem}%, TEMP={temp}°C, Detections={device.detection_count}"
            )
            return True
        return False

    def _device_loop(self, device: SimulatedDevice):
        """Main loop for a simulated device."""
        # Register device first
        if not self._register_device(device):
            print(f"[{device.device_id}] Failed to register, retrying...")
            time.sleep(5)
            if not self._register_device(device):
                print(f"[{device.device_id}] Registration failed, exiting")
                return

        # Send heartbeats and detections
        while not self._stop_event.is_set():
            self._send_heartbeat(device)

            # Randomly trigger detection
            if random.random() < self.detection_probability:
                self._send_detection(device)

            self._stop_event.wait(self.heartbeat_interval)

    def start(self):
        """Start the device simulator."""
        print("\n" + "=" * 60)
        print("OPTIC-SHIELD Device Simulator")
        print("=" * 60)
        print(f"API URL: {self.api_url}")
        print(f"Devices: {self.num_devices}")
        print(f"Heartbeat Interval: {self.heartbeat_interval}s")
        print(f"Detection Probability: {self.detection_probability}")
        print(f"Animal Category: {self.animal_category}")
        print(
            f"Wildlife Classes: {', '.join([w['name'] for w in self.wildlife_classes])}"
        )
        print(f"Send Images: {self.send_images}")
        print("=" * 60 + "\n")

        # Load demo images
        if self.send_images:
            self._load_demo_images()

        # Create devices
        for i in range(self.num_devices):
            device = self._create_device(i)
            self.devices.append(device)
            print(f"Created device: {device.name} ({device.device_id})")
            print(f"  Location: {device.location['name']}")
            print(f"  Hardware: {device.hardware_model}")
            print(f"  Cameras: {len(device.cameras)}")
            print()

        # Start device threads
        for device in self.devices:
            thread = threading.Thread(
                target=self._device_loop,
                args=(device,),
                name=f"Device-{device.device_id}",
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)
            time.sleep(0.5)  # Stagger device starts

        print(f"\nAll {self.num_devices} devices started. Press Ctrl+C to stop.\n")

    def stop(self):
        """Stop the device simulator."""
        print("\nStopping simulator...")
        self._stop_event.set()

        for thread in self._threads:
            thread.join(timeout=5)

        print("Simulator stopped.")

    def run(self):
        """Run the simulator until interrupted."""
        self.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def main():
    parser = argparse.ArgumentParser(description="OPTIC-SHIELD Device Simulator")
    parser.add_argument(
        "--api-url",
        type=str,
        default=os.getenv("OPTIC_DASHBOARD_URL", "http://localhost:3000"),
        help="Dashboard API URL",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("OPTIC_API_KEY", "development-key"),
        help="API key for authentication",
    )
    parser.add_argument(
        "--devices", type=int, default=3, help="Number of devices to simulate"
    )
    parser.add_argument(
        "--interval", type=int, default=10, help="Heartbeat interval in seconds"
    )
    parser.add_argument(
        "--detection-rate",
        type=float,
        default=0.1,
        help="Probability of detection per heartbeat (0-1)",
    )
    parser.add_argument(
        "--animal-category",
        type=str,
        choices=ANIMAL_CATEGORIES,
        default="leopard",
        help=f"Animal category to simulate detections for. Choices: {ANIMAL_CATEGORIES} (default: leopard)",
    )

    args = parser.parse_args()

    simulator = DeviceSimulator(
        api_url=args.api_url,
        api_key=args.api_key,
        num_devices=args.devices,
        heartbeat_interval=args.interval,
        detection_probability=args.detection_rate,
        animal_category=args.animal_category,
    )

    simulator.run()


if __name__ == "__main__":
    main()
