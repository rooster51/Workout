# Forge Fitness

A mobile-friendly Streamlit workout planner with deterministic daily workouts, 2–24 week progressive programs, Google sign-in, Firestore-backed multi-user data, body-weight trends, and exercise progress tracking.

## Structure

```text
app.py                    Streamlit UI and navigation
workout_app/models.py     Typed domain models
workout_app/data.py       80+ exercise catalog
workout_app/generator.py  Workout, substitution, and program rules
workout_app/storage.py    Safe local JSON persistence
tests/                    Generator tests
```

## Install and run

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Open the local URL shown in the terminal. To use it on a phone connected to the same Wi-Fi, run:

```powershell
py -m streamlit run app.py --server.address 0.0.0.0
```

Then open the Network URL shown by Streamlit on the phone. Windows Firewall may ask you to allow private-network access. For access away from home, deploy to Streamlit Community Cloud or another HTTPS host; do not expose a home port directly to the internet.

Run tests with `py -m pytest`.

## Google login and Firebase storage

The app stays in local demo mode until authentication is configured. For a deployed multi-user app:

1. Create a Google Cloud/Firebase project and enable Cloud Firestore.
2. Configure an OAuth 2.0 web client. Add `https://YOUR-APP.streamlit.app/oauth2callback` as an authorized redirect URI.
3. Create a minimally scoped service account with Firestore data access and generate a JSON key.
4. In Streamlit Community Cloud, open **App settings → Secrets**.
5. Copy the structure from `.streamlit/secrets.example.toml`, insert the OAuth and service-account values, and save.

Do not commit `.streamlit/secrets.toml` or the service-account JSON. The real secrets file is ignored by Git.

## MVP notes

- Local development without secrets uses user-scoped JSON in `.workout_data/`. Production with Firebase secrets uses a separate Firestore document tree for each Google identity.
- Exercise illustrations, accounts/cloud sync, notifications, and multi-device identity are intentionally omitted.
- Google OIDC login and Firestore provide multi-device identity and persistence once configured in Streamlit Secrets.
- Program progression uses conservative rep/load guidance and every-fourth-week recovery volume. It is general fitness guidance, not medical advice.
