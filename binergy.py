#!/usr/bin/env python3
"""
gpio17_to_homeassistant_webhook.py

Cron-friendly script:
- reads Raspberry Pi GPIO17 with internal pull-up (PC817 OUT -> GPIO17)
- posts the state to Home Assistant via webhook (Method A)

Webhook URL (provided):
  http://homeassistant.local:8123/api/webhook/bienergie

Notes:
- With PC817 + pull-up:
    No input signal -> GPIO HIGH  -> active=False
    Input active    -> GPIO LOW   -> active=True
"""

import json
import sys
import time
import urllib.request
import urllib.error
from typing import Optional

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(f"ERROR: RPi.GPIO import failed: {e}", file=sys.stderr)
    sys.exit(2)

# ----------------------------
# Settings
# ----------------------------
GPIO_PIN = 3  # BCM numbering (GPIO3). Physical pin is 5
DEVICE_NAME = "pi-zero-w"

HA_WEBHOOK_URL = "http://homeassistant:8123/api/webhook/hydro_rate_update"
HTTP_TIMEOUT_SECONDS = 8


def build_payload(level: int, active: bool) -> dict:
    return {
        "device": DEVICE_NAME,
        "gpio": GPIO_PIN,
        "level": int(level),      # 1=HIGH, 0=LOW
        "value": bool(active),   # True when input is active (LOW)
        "ts": int(time.time()),
    }


def read_gpio17_active_low() -> dict:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.IN)

    level = GPIO.input(GPIO_PIN)         # 1=HIGH, 0=LOW
    active = (level == GPIO.LOW)         # active when LOW
    return build_payload(level=level, active=active)


def http_post_json(url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        _ = resp.read()


def send_to_home_assistant(payload: dict) -> None:
    http_post_json(HA_WEBHOOK_URL, payload)


def parse_args(argv: list[str]) -> Optional[dict]:
    """
    Test modes (no GPIO required):
      --test-on   -> send active=True (simulates input active / GPIO LOW)
      --test-off  -> send active=False (simulates no input / GPIO HIGH)
    """
    if "--test-on" in argv:
        return build_payload(level=0, active=True)
    if "--test-off" in argv:
        return build_payload(level=1, active=False)
    return None


def main() -> int:
    payload = None
    try:
        payload = parse_args(sys.argv[1:]) or read_gpio17_active_low()
        send_to_home_assistant(payload)
        return 0
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}", file=sys.stderr)
        try:
            print(e.read().decode("utf-8", errors="ignore"), file=sys.stderr)
        except Exception:
            pass
        return 3
    except urllib.error.URLError as e:
        print(f"URLError: {e}", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        # Only cleanup if GPIO was likely used (not strictly required, but safe)
        try:
            GPIO.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

