import base64
import json
import os
import time
from urllib.request import Request, urlopen

ARTIST_ID = "3k0GVFDNK2SBNw3ICBJNEt"
TRACKS = {
    "nah": "7nE94YPRt7FoYA4vRbF3qg",
    "ldv": "36BgR3GousaABIrvClzYCv",
}

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"

def get_access_token(client_id: str, client_secret: str) -> str:
    creds = f"{client_id}:{client_secret}".encode("utf-8")
    b64 = base64.b64encode(creds).decode("utf-8")

    data = "grant_type=client_credentials".encode("utf-8")
    req = Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urlopen(req, timeout=20) as r:
        payload = json.loads(r.read().decode("utf-8"))
    return payload["access_token"]

def api_get(token: str, path: str) -> dict:
    req = Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    cid = os.environ["SPOTIFY_CLIENT_ID"]
    csec = os.environ["SPOTIFY_CLIENT_SECRET"]

    token = get_access_token(cid, csec)

    artist = api_get(token, f"/artists/{ARTIST_ID}")
    out = {
        "updated_unix": int(time.time()),
        "artist": {
            "name": artist.get("name"),
            "followers": artist.get("followers", {}).get("total"),
            "popularity": artist.get("popularity"),
        },
        "tracks": {}
    }

    for key, tid in TRACKS.items():
        tr = api_get(token, f"/tracks/{tid}")
        out["tracks"][key] = {
            "name": tr.get("name"),
            "popularity": tr.get("popularity"),
        }

    os.makedirs("docs", exist_ok=True)
    with open("docs/stats.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
