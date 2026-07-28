import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    app_id = "2180630959386928"
    app_secret = "0a3d7c4bd24e26f4464c833e33968010"
    token = "EAAeZCRbW4cTABR8bLcT2kue3CZChrZA2ZCr1CZCuiAVJ5mcFR1qw2rww9lCisz41dwnXUNoxQeIADmBF70Ji97wxLa8dQU45vcsQRORAwK46ZAd2DcgTKeSM8Rj0Xys7lDIuMBvxY9u5OV9ObDdcVJZBmQhMOxab4WuRRmttqjDJyLsamMRuzZCxZAbtrpqDzYAJTfBtfE5JCKCsPl1Ye05AeTUho5o63r6NdFvjCNagZAXTAV7J4FwcZCVZcpsOK7VRj7HwkGaFiDZA00Bva58F7PIUZBKpzx"
    
    debug_url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": token,
        "access_token": f"{app_id}|{app_secret}"
    }
    
    res = requests.get(debug_url, params=params)
    print("Status:", res.status_code)
    if res.status_code == 200:
        data = res.json().get("data", {})
        print("Token Info:")
        print("  Is Valid:", data.get("is_valid"))
        print("  Scopes:", data.get("scopes"))
        print("  Expires At:", data.get("expires_at"))
        print("  User ID:", data.get("user_id"))
        print("  Application ID:", data.get("application"))
    else:
        print("Error debugging token:")
        print(res.text)

if __name__ == "__main__":
    main()
