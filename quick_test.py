#!/usr/bin/env python3
"""Smoke-test a local NepSewa server (start `python main.py` in another terminal first)."""

import time
import sys

import requests


def test_endpoints():
    base_url = f"http://127.0.0.1:{int(sys.argv[1]) if len(sys.argv) > 1 else 8001}"

    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Home Page", f"{base_url}/"),
        ("Services Page", f"{base_url}/services"),
        ("Top Professionals", f"{base_url}/api/top-professionals"),
        ("Services API", f"{base_url}/api/services"),
        ("Providers API", f"{base_url}/api/providers"),
    ]

    print(f"Testing {base_url} ...")
    time.sleep(0.5)

    for name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            ok = response.status_code == 200
            print(f"{'OK' if ok else 'FAIL'} {name} ({response.status_code})")
        except Exception as e:
            print(f"FAIL {name}: {e}")


if __name__ == "__main__":
    test_endpoints()
