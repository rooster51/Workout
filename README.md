# Forge Fitness

A mobile-friendly Streamlit workout planner with deterministic, rule-based daily workouts and 2–24 week progressive programs. Data stays on the machine running Streamlit; no paid backend or API is required.

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

## MVP notes

- Settings, completed workouts, and programs are stored as JSON in `.workout_data/` on the server.
- Exercise illustrations, accounts/cloud sync, notifications, and multi-device identity are intentionally omitted.
- A deployed shared instance needs authentication and per-user storage before use by multiple people.
- Program progression uses conservative rep/load guidance and every-fourth-week recovery volume. It is general fitness guidance, not medical advice.
