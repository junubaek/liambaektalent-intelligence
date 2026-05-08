from connectors.gdrive_api import GDriveConnector
import sys

def test_auth():
    print("Initializing GDriveConnector...")
    try:
        g = GDriveConnector()
        print("Success! GDrive service initialized.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_auth()
