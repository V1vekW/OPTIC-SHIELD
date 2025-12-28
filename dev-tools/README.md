# OPTIC-SHIELD Development Tools

Development and testing scripts for the OPTIC-SHIELD dashboard. These scripts are **NOT** needed on the actual Raspberry Pi device.

## Scripts

### `api_test.py` - API Testing Suite
Interactive testing tool for dashboard APIs.

**Usage:**
```bash
# Interactive menu
python3 api_test.py --url https://your-dashboard.vercel.app --api-key YOUR_API_KEY

# Run all tests
python3 api_test.py --url https://your-dashboard.vercel.app --api-key YOUR_API_KEY --run-all

# Emulate a device
python3 api_test.py --url https://your-dashboard.vercel.app --api-key YOUR_API_KEY --emulate
```

### `device_simulator.py` - Device Simulator
Simulates multiple devices sending telemetry to the dashboard.

**Usage:**
```bash
python3 device_simulator.py --api-url https://your-dashboard.vercel.app --api-key YOUR_API_KEY --devices 3 --animal-category leopard
```

### `run_tests.py` - Setup Validation Tests
Runs validation tests for device setup.

## API Key
The `--api-key` parameter should match the `API_SECRET_KEY` environment variable configured in your Vercel dashboard.

For local development, use `development-key`.
