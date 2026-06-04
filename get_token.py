import requests

url = "https://kauth.kakao.com/oauth/token"
data = {
    "grant_type": "authorization_code",
    "client_id": "3791bbf5d2e9b1d9b12cece3da1cf583",
    "redirect_uri": "https://localhost",
    "code": "u9_dRNTsufD7KUPluaGxds3SVW-BGdZj_BMnnZkLF5k31WIZwz9DRgAAAAQKFxafAAABnpDKseTNsk3jZ7dWzg"
}

response = requests.post(url, data=data)
print("=== 발급된 카카오 토큰 정보 ===")
print(response.text)
