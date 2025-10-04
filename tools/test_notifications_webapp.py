#!/usr/bin/env python3
"""
Test the complete notifications webapp functionality.
"""

import requests


def test_notifications_webapp():
    """Test the complete notifications webapp."""
    base_url = "http://localhost:8001"

    print("🚀 Testing PulseAI Notifications WebApp...")
    print("=" * 50)

    # Test 1: Check that the notifications page loads
    print("\n1. Testing notifications page...")
    try:
        response = requests.get(f"{base_url}/notifications")
        if response.status_code == 200:
            print("✅ Notifications page loads successfully")
            if "PulseAI - Notifications" in response.text:
                print("✅ Page title is correct")
            else:
                print("⚠️  Page title might be incorrect")
        else:
            print(f"❌ Notifications page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Notifications page error: {e}")
        return False

    # Test 2: Test API endpoint
    print("\n2. Testing API endpoint...")
    try:
        response = requests.get(f"{base_url}/api/user_notifications?user_id=123&limit=10")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                notifications = data.get('data', {}).get('notifications', [])
                print(f"✅ API returns {len(notifications)} notifications")

                if notifications:
                    print("✅ Sample notification:")
                    sample = notifications[0]
                    print(f"   - Title: {sample.get('title', 'N/A')}")
                    print(f"   - Read: {sample.get('read', 'N/A')}")
                    print(f"   - ID: {sample.get('id', 'N/A')}")
                else:
                    print("⚠️  No notifications found")
            else:
                print(f"❌ API error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

    # Test 3: Test mark as read functionality
    print("\n3. Testing mark as read functionality...")
    try:
        # First get notifications to find one to mark as read
        response = requests.get(f"{base_url}/api/user_notifications?user_id=123&limit=5")
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('data', {}).get('notifications', [])

            if notifications:
                # Find an unread notification
                unread_notification = None
                for notification in notifications:
                    if not notification.get('read', True):
                        unread_notification = notification
                        break

                if unread_notification:
                    notification_id = unread_notification['id']
                    print(f"✅ Found unread notification: {notification_id}")

                    # Mark as read
                    mark_response = requests.post(
                        f"{base_url}/api/user_notifications/mark_read",
                        headers={'Content-Type': 'application/json'},
                        json={'notification_id': notification_id},
                    )

                    if mark_response.status_code == 200:
                        mark_data = mark_response.json()
                        if mark_data.get('status') == 'success' and mark_data.get('data', {}).get(
                            'success'
                        ):
                            print("✅ Successfully marked notification as read")
                        else:
                            print(f"⚠️  Mark as read returned: {mark_data}")
                    else:
                        print(f"❌ Mark as read failed: {mark_response.status_code}")
                else:
                    print("⚠️  No unread notifications found to test")
            else:
                print("⚠️  No notifications found for testing")
        else:
            print(f"❌ Failed to get notifications for testing: {response.status_code}")
    except Exception as e:
        print(f"❌ Mark as read test error: {e}")

    # Test 4: Test error handling
    print("\n4. Testing error handling...")
    try:
        # Test with invalid notification ID
        response = requests.post(
            f"{base_url}/api/user_notifications/mark_read",
            headers={'Content-Type': 'application/json'},
            json={'notification_id': 'invalid-id'},
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and not data.get('data', {}).get('success'):
                print("✅ Error handling works correctly")
            else:
                print(f"⚠️  Unexpected response for invalid ID: {data}")
        else:
            print(f"❌ Error handling test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test error: {e}")

    print("\n" + "=" * 50)
    print("✅ Notifications WebApp testing completed!")
    return True


def main():
    """Main function."""
    try:
        test_notifications_webapp()
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")


if __name__ == "__main__":
    main()
