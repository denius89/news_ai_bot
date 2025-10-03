#!/usr/bin/env python3
"""
Test API directly by making HTTP requests.
"""

import requests
import json


def test_api_direct():
    """Test API by making HTTP requests."""

    base_url = "http://localhost:8001"

    print("🔍 Testing API directly...")

    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test 2: Get notifications
    print("\n2. Testing get notifications...")
    try:
        response = requests.get(f"{base_url}/api/user_notifications?user_id=123&limit=10")
        print(f"✅ Get notifications: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        notifications = data.get('data', {}).get('notifications', [])
        print(f"Found {len(notifications)} notifications")

    except Exception as e:
        print(f"❌ Get notifications failed: {e}")
        return False

    # Test 3: Mark notification as read
    print("\n3. Testing mark notification as read...")
    try:
        # First get a notification ID
        if notifications:
            notification_id = notifications[0]['id']
            print(f"Using notification ID: {notification_id}")

            response = requests.post(
                f"{base_url}/api/user_notifications/mark_read",
                headers={'Content-Type': 'application/json'},
                json={'notification_id': notification_id},
            )
            print(f"✅ Mark as read: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print("⚠️  No notifications to mark as read")

    except Exception as e:
        print(f"❌ Mark as read failed: {e}")
        return False

    return True


def main():
    """Main function."""
    print("🚀 Testing API directly...")
    print("=" * 50)

    success = test_api_direct()

    print("=" * 50)
    if success:
        print("✅ Test completed!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
