import os
import requests

# Use the live API to fix tickets
API_URL = "https://test-backend-eosin.vercel.app"

def recreate_tickets():
    try:
        # Login as admin first
        login_data = {
            "email": "admin@company.com",
            "password": "admin123"
        }
        
        print("Logging in as admin...")
        response = requests.post(f"{API_URL}/api/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        token = response.json().get('access_token')
        if not token:
            print("❌ No access token received")
            return
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-CSRF-Token': 'recreate-tickets-action'
        }
        
        print("Recreating tickets...")
        response = requests.post(f"{API_URL}/api/admin/recreate-tickets", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            print(f"✅ Created {result['tickets_created']} tickets")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recreate_tickets()