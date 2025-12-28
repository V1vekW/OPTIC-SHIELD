#!/usr/bin/env python3
"""
OPTIC-SHIELD API Testing Suite
Comprehensive testing script for Dashboard device emulation APIs.
Test all API endpoints individually or run a full test suite with reporting.
"""

import os
import sys
import json
import time
import random
import argparse
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import urllib.request
import urllib.error


# ANSI colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


# Test configuration
DEFAULT_DEVICE_ID = f"test-{random.randint(1000,9999)}"
WILD_CAT_SPECIES = [
    "leopard",
    "tiger",
    "jaguar",
    "lion",
    "cheetah",
    "snow leopard",
    "clouded leopard",
    "puma",
    "lynx",
]


class TestResult:
    """Represents a single test result."""

    def __init__(
        self,
        name: str,
        passed: bool,
        status_code: int,
        message: str,
        response_time_ms: float,
        details: Optional[Dict] = None,
    ):
        self.name = name
        self.passed = passed
        self.status_code = status_code
        self.message = message
        self.response_time_ms = response_time_ms
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class APITester:
    """Testing suite for OPTIC-SHIELD Dashboard APIs."""

    def __init__(self, base_url: str, api_key: str, device_id: str = DEFAULT_DEVICE_ID):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.device_id = device_id
        self.results: List[TestResult] = []
        self._demo_image: Optional[str] = None
        self._load_demo_image()

    def _load_demo_image(self):
        """Load a demo image for testing."""
        demo_dir = Path(__file__).parent.parent / "demo-img"
        for image_name in ["jaguar.jpg", "lion.png"]:
            image_path = demo_dir / image_name
            if image_path.exists():
                try:
                    with open(image_path, "rb") as f:
                        self._demo_image = base64.b64encode(f.read()).decode()
                    print(
                        f"{Colors.GREEN}✓{Colors.END} Loaded demo image: {image_name}"
                    )
                    return
                except Exception as e:
                    print(
                        f"{Colors.YELLOW}⚠{Colors.END} Failed to load {image_name}: {e}"
                    )
        print(
            f"{Colors.YELLOW}⚠{Colors.END} No demo images found, detection tests will run without images"
        )

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict] = None
    ) -> Tuple[Optional[Dict], int, float]:
        """Make an HTTP request and return response, status code, and response time."""
        url = f"{self.base_url}{endpoint}"
        payload = json.dumps(data) if data else None

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Device-ID": self.device_id,
            "X-Timestamp": str(int(time.time())),
        }

        start_time = time.time()

        try:
            req = urllib.request.Request(
                url,
                data=payload.encode() if payload else None,
                headers=headers,
                method=method,
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                response_time_ms = (time.time() - start_time) * 1000
                response_data = response.read().decode()
                return (
                    json.loads(response_data) if response_data else {},
                    response.status,
                    response_time_ms,
                )

        except urllib.error.HTTPError as e:
            response_time_ms = (time.time() - start_time) * 1000
            try:
                error_body = e.read().decode()
                error_data = json.loads(error_body) if error_body else {}
            except:
                error_data = {"error": str(e.reason)}
            return error_data, e.code, response_time_ms
        except urllib.error.URLError as e:
            response_time_ms = (time.time() - start_time) * 1000
            return {"error": str(e.reason)}, 0, response_time_ms
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return {"error": str(e)}, 0, response_time_ms

    def _add_result(
        self,
        name: str,
        passed: bool,
        status_code: int,
        message: str,
        response_time: float,
        details: Optional[Dict] = None,
    ):
        """Add a test result."""
        result = TestResult(name, passed, status_code, message, response_time, details)
        self.results.append(result)

        status_icon = (
            f"{Colors.GREEN}✓ PASS{Colors.END}"
            if passed
            else f"{Colors.RED}✗ FAIL{Colors.END}"
        )
        print(f"  {status_icon} {name} ({status_code}, {response_time:.0f}ms)")
        if not passed and details:
            print(
                f"       {Colors.RED}Error: {details.get('error', message)}{Colors.END}"
            )

    # ==================== TEST METHODS ====================

    def test_device_registration(self) -> bool:
        """Test POST /api/devices - Device registration."""
        print(f"\n{Colors.CYAN}Testing Device Registration API...{Colors.END}")

        data = {
            "device_id": self.device_id,
            "info": {
                "name": f"Test-Device-{self.device_id}",
                "location": {
                    "name": "Test Location",
                    "latitude": 18.5204,
                    "longitude": 73.8567,
                    "timezone": "Asia/Kolkata",
                },
                "version": "1.0.0-test",
                "hardware_model": "Test Hardware",
                "environment": "development",
                "tags": ["test", "api-test"],
                "cameras": [
                    {
                        "id": "cam-test-1",
                        "name": "Test Camera",
                        "model": "Test Model",
                        "resolution": "1920x1080",
                        "status": "active",
                    }
                ],
            },
        }

        response, status_code, response_time = self._make_request(
            "/api/devices", "POST", data
        )
        passed = status_code == 200 and response.get("success", False)

        self._add_result(
            "Device Registration",
            passed,
            status_code,
            response.get("message", "No message"),
            response_time,
            response if not passed else None,
        )
        return passed

    def test_heartbeat(self) -> bool:
        """Test POST /api/devices/heartbeat - Device heartbeat."""
        print(f"\n{Colors.CYAN}Testing Heartbeat API...{Colors.END}")

        data = {
            "device_id": self.device_id,
            "timestamp": time.time(),
            "status": "online",
            "stats": {
                "uptime_seconds": random.randint(1000, 100000),
                "detection_count": random.randint(0, 100),
                "system": {
                    "cpu_percent": random.uniform(10, 80),
                    "memory_percent": random.uniform(30, 70),
                    "memory_used_mb": random.randint(500, 2000),
                    "memory_total_mb": 4096,
                    "temperature_celsius": random.uniform(40, 60),
                    "disk_percent": random.uniform(20, 60),
                    "disk_used_gb": random.uniform(5, 30),
                    "disk_total_gb": 64,
                },
                "power": {
                    "consumption_watts": random.uniform(3, 8),
                    "source": "ac",
                    "battery_percent": None,
                },
                "cameras": [
                    {
                        "id": "cam-test-1",
                        "name": "Test Camera",
                        "model": "Test",
                        "resolution": "1080p",
                        "status": "active",
                    }
                ],
                "network": {"latency_ms": random.randint(20, 100)},
            },
            "info": {
                "name": f"Test-Device-{self.device_id}",
                "location": {
                    "name": "Test Location",
                    "latitude": 18.52,
                    "longitude": 73.85,
                },
            },
        }

        response, status_code, response_time = self._make_request(
            "/api/devices/heartbeat", "POST", data
        )
        passed = status_code == 200 and response.get("success", False)

        self._add_result(
            "Heartbeat API",
            passed,
            status_code,
            response.get("message", "No message"),
            response_time,
            response if not passed else None,
        )
        return passed

    def test_detection(self) -> bool:
        """Test POST /api/devices/detections - Send detection."""
        print(f"\n{Colors.CYAN}Testing Detection API...{Colors.END}")

        detection_id = int(time.time() * 1000)
        species = random.choice(WILD_CAT_SPECIES)

        data = {
            "event_id": f"evt-{detection_id}",
            "detection_id": detection_id,
            "device_id": self.device_id,
            "camera_id": "cam-test-1",
            "timestamp": time.time(),
            "class_name": species,
            "confidence": random.uniform(0.75, 0.98),
            "bbox": [100, 100, 400, 400],
            "location": {
                "name": "Test Location",
                "latitude": 18.5204,
                "longitude": 73.8567,
            },
            "metadata": {
                "priority": "high",
                "processing_time_ms": random.randint(100, 300),
                "model_version": "yolov8n",
                "camera_name": "Test Camera",
            },
        }

        if self._demo_image:
            data["image_base64"] = self._demo_image

        response, status_code, response_time = self._make_request(
            "/api/devices/detections", "POST", data
        )
        passed = status_code == 200 and response.get("success", False)

        self._add_result(
            f"Detection API ({species})",
            passed,
            status_code,
            response.get("message", "No message"),
            response_time,
            (
                response
                if not passed
                else {"species": species, "has_image": bool(self._demo_image)}
            ),
        )
        return passed

    def test_device_list(self) -> bool:
        """Test GET /api/devices - List all devices."""
        print(f"\n{Colors.CYAN}Testing Device List API...{Colors.END}")

        response, status_code, response_time = self._make_request("/api/devices", "GET")
        passed = status_code == 200 and response.get("success", False)

        device_count = len(response.get("devices", [])) if passed else 0

        self._add_result(
            "Device List API",
            passed,
            status_code,
            f"Found {device_count} devices",
            response_time,
            response if not passed else {"device_count": device_count},
        )
        return passed

    def test_detection_logs(self) -> bool:
        """Test GET /api/devices/detections - Get detection logs."""
        print(f"\n{Colors.CYAN}Testing Detection Logs API...{Colors.END}")

        response, status_code, response_time = self._make_request(
            f"/api/devices/detections?device_id={self.device_id}&limit=10", "GET"
        )
        passed = status_code == 200 and response.get("success", False)

        log_count = len(response.get("logs", [])) if passed else 0

        self._add_result(
            "Detection Logs API",
            passed,
            status_code,
            f"Found {log_count} logs",
            response_time,
            response if not passed else {"log_count": log_count},
        )
        return passed

    def run_all_tests(self) -> bool:
        """Run all API tests."""
        print(
            f"\n{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(
            f"{Colors.BOLD}{Colors.HEADER}     OPTIC-SHIELD API Test Suite - Full Run{Colors.END}"
        )
        print(
            f"{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(f"Dashboard URL: {self.base_url}")
        print(f"Test Device ID: {self.device_id}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.results = []  # Reset results

        # Run tests in order
        self.test_device_registration()
        time.sleep(0.5)
        self.test_heartbeat()
        time.sleep(0.5)
        self.test_detection()
        time.sleep(0.5)
        self.test_device_list()
        time.sleep(0.5)
        self.test_detection_logs()

        return self.print_report()

    def print_report(self) -> bool:
        """Print a detailed test report."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        all_passed = passed == total

        print(
            f"\n{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(f"{Colors.BOLD}                    TEST REPORT{Colors.END}")
        print(
            f"{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(f"Dashboard URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n{'Test':<30} {'Status':<10} {'Code':<8} {'Time':<10}")
        print("─" * 60)

        for r in self.results:
            status = (
                f"{Colors.GREEN}PASS{Colors.END}"
                if r.passed
                else f"{Colors.RED}FAIL{Colors.END}"
            )
            print(
                f"{r.name:<30} {status:<18} {r.status_code:<8} {r.response_time_ms:.0f}ms"
            )

        print("─" * 60)

        if all_passed:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✓ Summary: {passed}/{total} tests passed{Colors.END}"
            )
        else:
            print(
                f"\n{Colors.RED}{Colors.BOLD}✗ Summary: {passed}/{total} tests passed{Colors.END}"
            )

        print(
            f"{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}\n"
        )

        return all_passed

    def emulate_device(
        self,
        device_name: str,
        location_name: str,
        animal_category: str,
        interval: int = 10,
        detection_rate: float = 0.3,
    ):
        """Emulate a device continuously to a production portal."""
        print(
            f"\n{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(
            f"{Colors.BOLD}{Colors.HEADER}     OPTIC-SHIELD Device Emulation{Colors.END}"
        )
        print(
            f"{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
        )
        print(f"Dashboard URL: {self.base_url}")
        print(f"Device ID: {self.device_id}")
        print(f"Device Name: {device_name}")
        print(f"Location: {location_name}")
        print(f"Animal Category: {animal_category}")
        print(f"Heartbeat Interval: {interval}s")
        print(f"Detection Rate: {detection_rate}")
        print(f"\nPress Ctrl+C to stop emulation.\n")

        # Register device first
        reg_data = {
            "device_id": self.device_id,
            "info": {
                "name": device_name,
                "location": {
                    "name": location_name,
                    "latitude": 18.52,
                    "longitude": 73.85,
                    "timezone": "Asia/Kolkata",
                },
                "version": "1.0.0",
                "hardware_model": "Raspberry Pi 5",
                "environment": "production",
                "tags": ["wildlife", animal_category],
                "cameras": [
                    {
                        "id": f"cam-{self.device_id}",
                        "name": "Camera 1",
                        "model": "Pi Camera 3",
                        "resolution": "1920x1080",
                        "status": "active",
                    }
                ],
            },
        }

        response, status, _ = self._make_request("/api/devices", "POST", reg_data)
        if status == 200:
            print(f"{Colors.GREEN}✓ Device registered successfully{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Failed to register device: {response}{Colors.END}")
            return

        # Select species based on category
        if animal_category == "leopard":
            species_list = ["leopard", "snow leopard", "clouded leopard"]
        else:
            species_list = WILD_CAT_SPECIES

        detection_count = 0
        heartbeat_count = 0

        try:
            while True:
                # Send heartbeat
                heartbeat_data = {
                    "device_id": self.device_id,
                    "timestamp": time.time(),
                    "status": "online",
                    "stats": {
                        "uptime_seconds": (heartbeat_count + 1) * interval,
                        "detection_count": detection_count,
                        "system": {
                            "cpu_percent": random.uniform(15, 45),
                            "memory_percent": random.uniform(40, 60),
                            "memory_used_mb": random.randint(1500, 2500),
                            "memory_total_mb": 4096,
                            "temperature_celsius": random.uniform(42, 55),
                            "disk_percent": random.uniform(20, 40),
                            "disk_used_gb": random.uniform(8, 20),
                            "disk_total_gb": 64,
                        },
                        "power": {
                            "consumption_watts": random.uniform(4, 7),
                            "source": "ac",
                            "battery_percent": None,
                        },
                        "cameras": [
                            {
                                "id": f"cam-{self.device_id}",
                                "name": "Camera 1",
                                "model": "Pi Camera 3",
                                "resolution": "1080p",
                                "status": "active",
                            }
                        ],
                        "network": {"latency_ms": random.randint(30, 100)},
                    },
                }

                response, status, resp_time = self._make_request(
                    "/api/devices/heartbeat", "POST", heartbeat_data
                )
                heartbeat_count += 1
                status_icon = (
                    f"{Colors.GREEN}✓{Colors.END}"
                    if status == 200
                    else f"{Colors.RED}✗{Colors.END}"
                )
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] {status_icon} Heartbeat #{heartbeat_count} ({resp_time:.0f}ms)"
                )

                # Possibly send detection
                if random.random() < detection_rate:
                    species = random.choice(species_list)
                    det_data = {
                        "event_id": f"evt-{int(time.time() * 1000)}",
                        "detection_id": int(time.time() * 1000),
                        "device_id": self.device_id,
                        "camera_id": f"cam-{self.device_id}",
                        "timestamp": time.time(),
                        "class_name": species,
                        "confidence": random.uniform(0.75, 0.96),
                        "bbox": [
                            random.randint(50, 150),
                            random.randint(50, 150),
                            random.randint(350, 550),
                            random.randint(350, 550),
                        ],
                        "location": {
                            "name": location_name,
                            "latitude": 18.52,
                            "longitude": 73.85,
                        },
                        "metadata": {
                            "priority": "high",
                            "processing_time_ms": random.randint(80, 250),
                            "model_version": "yolov8n",
                        },
                    }
                    if self._demo_image:
                        det_data["image_base64"] = self._demo_image

                    response, status, resp_time = self._make_request(
                        "/api/devices/detections", "POST", det_data
                    )
                    detection_count += 1
                    status_icon = (
                        f"{Colors.GREEN}✓{Colors.END}"
                        if status == 200
                        else f"{Colors.RED}✗{Colors.END}"
                    )
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] {status_icon} Detection: {Colors.YELLOW}{species}{Colors.END} sent ({resp_time:.0f}ms)"
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Emulation stopped.{Colors.END}")
            print(f"Total heartbeats: {heartbeat_count}")
            print(f"Total detections: {detection_count}")


def print_menu():
    """Print the interactive menu."""
    print(
        f"\n{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
    )
    print(
        f"{Colors.BOLD}{Colors.HEADER}     OPTIC-SHIELD API Testing Suite{Colors.END}"
    )
    print(
        f"{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════{Colors.END}"
    )
    print(f"\n{Colors.BOLD}Select an option:{Colors.END}")
    print(f"  {Colors.CYAN}1.{Colors.END} Test Device Registration API")
    print(f"  {Colors.CYAN}2.{Colors.END} Test Heartbeat API")
    print(f"  {Colors.CYAN}3.{Colors.END} Test Detection API")
    print(f"  {Colors.CYAN}4.{Colors.END} Test Device List API (GET)")
    print(f"  {Colors.CYAN}5.{Colors.END} Test Detection Logs API (GET)")
    print(f"  {Colors.GREEN}6.{Colors.END} Run ALL Tests")
    print(f"  {Colors.YELLOW}7.{Colors.END} Emulate Device to Production Portal")
    print(f"  {Colors.RED}0.{Colors.END} Exit")
    print(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════════{Colors.END}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="OPTIC-SHIELD API Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_test.py --url https://your-dashboard.vercel.app --api-key your-api-key
  python api_test.py --url http://localhost:3000 --api-key development-key --run-all
  python api_test.py --url https://optic-shield.vercel.app --api-key prod-key --emulate
        """,
    )
    parser.add_argument(
        "--url",
        type=str,
        default=os.getenv("OPTIC_DASHBOARD_URL", "http://localhost:3000"),
        help="Dashboard URL to test against",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("OPTIC_API_KEY", "development-key"),
        help="API key for authentication",
    )
    parser.add_argument(
        "--device-id",
        type=str,
        default=DEFAULT_DEVICE_ID,
        help="Device ID to use for testing",
    )
    parser.add_argument(
        "--run-all", action="store_true", help="Run all tests automatically and exit"
    )
    parser.add_argument(
        "--emulate", action="store_true", help="Start device emulation mode"
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}Dashboard URL:{Colors.END} {args.url}")
    print(
        f"{Colors.BOLD}API Key:{Colors.END} {args.api_key[:10]}..."
        if len(args.api_key) > 10
        else f"{Colors.BOLD}API Key:{Colors.END} {args.api_key}"
    )

    tester = APITester(args.url, args.api_key, args.device_id)

    # Run all tests if --run-all flag is set
    if args.run_all:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)

    # Start emulation if --emulate flag is set
    if args.emulate:
        device_name = (
            input(f"\n{Colors.CYAN}Enter device name:{Colors.END} ")
            or f"Emulated-{args.device_id}"
        )
        location_name = (
            input(f"{Colors.CYAN}Enter location name:{Colors.END} ") or "Test Location"
        )
        category = (
            input(
                f"{Colors.CYAN}Enter animal category (leopard/all_cats):{Colors.END} "
            )
            or "leopard"
        )
        tester.emulate_device(device_name, location_name, category)
        return

    # Interactive menu loop
    while True:
        print_menu()

        try:
            choice = input(f"\n{Colors.CYAN}Enter choice (0-7):{Colors.END} ").strip()
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Goodbye!{Colors.END}")
            break

        if choice == "0":
            print(f"\n{Colors.CYAN}Goodbye!{Colors.END}")
            break
        elif choice == "1":
            tester.test_device_registration()
        elif choice == "2":
            tester.test_heartbeat()
        elif choice == "3":
            tester.test_detection()
        elif choice == "4":
            tester.test_device_list()
        elif choice == "5":
            tester.test_detection_logs()
        elif choice == "6":
            tester.run_all_tests()
        elif choice == "7":
            device_name = (
                input(f"\n{Colors.CYAN}Enter device name:{Colors.END} ")
                or f"Emulated-{args.device_id}"
            )
            location_name = (
                input(f"{Colors.CYAN}Enter location name:{Colors.END} ")
                or "Test Location"
            )
            category = (
                input(
                    f"{Colors.CYAN}Enter animal category (leopard/all_cats):{Colors.END} "
                )
                or "leopard"
            )
            tester.emulate_device(device_name, location_name, category)
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 0-7.{Colors.END}")

        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


if __name__ == "__main__":
    main()
