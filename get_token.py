import requests

url = "https://kauth.kakao.com/oauth/token"
data = {
    "grant_type": "authorization_code",
    "client_id": "9fe627ca757d13776ce0c25d19abd2fd",
    "redirect_uri": "https://localhost",
    "code": "jzO9zc-JjlBXWDSWBcIohGZ6Era8ahRsyKDZmzy0dKt6BG1QJg6u-QAAAAQKFzVXAAABnpA5A3xPBWDH3LuH7A"
}

response = requests.post(url, data=data)
print("jzO9zc-JjlBXWDSWBcIohGZ6Era8ahRsyKDZmzy0dKt6BG1QJg6u-QAAAAQKFzVXAAABnpA5A3xPBWDH3LuH7A")
print(response.text)
