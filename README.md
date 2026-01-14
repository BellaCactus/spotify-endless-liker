<div align="center">

# <3 spotify endless liker

spotify api script using oauth.  
keeps credentials out of the repo.

![python](https://img.shields.io/badge/python-3.x-ff78c8?style=for-the-badge)
![spotify](https://img.shields.io/badge/api-spotify-0b0b0b?style=for-the-badge)
![vibe](https://img.shields.io/badge/vibe-terminal--core-ff4db8?style=for-the-badge)

</div>

---

## setup

```bash
pip install -r requirements.txt
```

set env vars (see `.env.example`):

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI` (example: `http://127.0.0.1:8000/callback`)

## run

```bash
python .\src\spotify_endless_liker.py
```

## note

oauth will open a browser login the first time.
