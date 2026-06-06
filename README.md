# FitForm AI

**Real-time exercise form correction powered by computer vision — built for people who train without a coach.**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00?style=flat-square&logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## Overview

FitForm AI is a web application that uses your webcam to watch you exercise in real time. It detects body posture using MediaPipe's pose estimation model, calculates joint angles, and gives you immediate feedback on your form — whether you're doing squats, push-ups, or bicep curls. Reps are counted automatically, and each session is saved to a personal dashboard with accuracy scores and calorie estimates.

The project started as a way to solve a real problem: most people training at home have no way to know if their form is correct. A gym trainer watches your knees, your back alignment, your elbow angle. This app does the same thing computationally.

---

## Features

- **Real-time pose detection** — MediaPipe Pose extracts 33 body landmarks at ~6 fps via the browser webcam
- **Form analysis** — joint angles are calculated at each frame and compared against exercise-specific thresholds
- **Automatic rep counting** — a state machine tracks up/down transitions per exercise
- **Live feedback** — context-aware messages like "Go Lower", "Keep Back Straight", "Arms Not Fully Extended"
- **Three exercises supported** — Squats, Push-ups, Bicep Curls
- **User authentication** — secure signup/login with Werkzeug password hashing and Flask-Login sessions
- **Workout dashboard** — weekly rep chart, exercise breakdown, session history table, streak tracker
- **Calories estimation** — MET-based approximation per exercise type
- **Dark mode** — full theme switch, preference saved in localStorage
- **Responsive layout** — sidebar dashboard works on tablets and smaller screens

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.0, Flask-Login, Flask-SQLAlchemy |
| AI / Computer Vision | MediaPipe Pose, OpenCV 4.10, NumPy |
| Frontend | HTML5, Vanilla CSS (custom properties), Vanilla JavaScript |
| Charts | Chart.js 4 (CDN) |
| Database | SQLite via SQLAlchemy ORM |
| Auth | Werkzeug password hashing, Flask-Login session management |
| Font | Inter (Google Fonts) |

---

## How the Form Detection Works

The webcam feed is captured in the browser using `getUserMedia`. Every 150ms, a JPEG frame is encoded as base64 and sent to the Flask backend via a POST request to `/workout/api/analyze`.

On the server:

1. The frame is decoded and passed to **MediaPipe Pose**, which returns 33 normalized (x, y) landmark coordinates
2. **Joint angles** are calculated using the dot product / arccos formula at the relevant joints (e.g., hip-knee-ankle for squats)
3. These angles are compared against **exercise-specific thresholds** to determine the current stage (up / down) and detect form issues
4. A **state machine** tracks stage transitions to count reps (down → up = 1 rep)
5. An accuracy score and feedback string are returned as JSON
6. The annotated frame (with skeleton drawn) is also returned and displayed over the canvas element

```
Browser (getUserMedia)
  → JPEG frame every 150ms
  → POST /workout/api/analyze (base64)
       → MediaPipe: extract 33 landmarks
       → Angle calculator: joint angles
       → Exercise analyzer: stage + feedback + accuracy
       → Rep counter: update state machine
  ← JSON: { reps, feedback, accuracy, stage, frame }
  → Update canvas overlay + UI counters
```

### Joint Angle Thresholds

| Exercise | Joint | Down (deg) | Up (deg) | Key feedback |
|---|---|---|---|---|
| Squat | hip-knee-ankle | ≤ 90 | ≥ 160 | Go Lower, Keep Back Straight |
| Push-up | shoulder-elbow-wrist | ≤ 90 | ≥ 160 | Go Lower, Arms Not Fully Extended |
| Bicep Curl | shoulder-elbow-wrist | ≥ 160 | ≤ 50 | Curl Higher, Fully Extend Your Arm |

---

## Project Structure

```
ai fitness/
├── app.py                        # Flask app factory, blueprint registration
├── config.py                     # App config, calorie constants
├── requirements.txt
├── run.bat                       # Windows one-click startup script
├── .env
│
├── ai/
│   ├── pose_detector.py          # MediaPipe Pose wrapper
│   ├── angle_calculator.py       # arccos joint angle calculation
│   ├── exercise_analyzer.py      # Per-exercise form logic and thresholds
│   └── rep_counter.py            # State machine rep counter
│
├── backend/
│   ├── models/
│   │   ├── user.py               # User model (Flask-Login + Werkzeug)
│   │   └── session.py            # WorkoutSession model
│   ├── auth/
│   │   └── routes.py             # /auth/signup, /auth/login, /auth/logout
│   ├── dashboard/
│   │   └── routes.py             # /, /api/stats, /api/history
│   └── workout/
│       └── routes.py             # /workout/, /workout/api/analyze, /workout/api/save
│
├── static/
│   ├── css/
│   │   ├── main.css              # Design system (CSS custom properties, layout)
│   │   ├── auth.css              # Login / signup card styles
│   │   └── dashboard.css        # Dashboard grid, webcam overlay, workout page
│   └── js/
│       ├── theme.js              # Dark mode toggle, localStorage persistence
│       ├── auth.js               # Password strength meter, show/hide toggle
│       ├── dashboard.js          # Chart.js charts, stats and history fetch
│       └── workout.js            # Webcam capture, frame POST, live UI updates
│
└── templates/
    ├── base.html                 # Shared layout (sidebar, topbar, flash messages)
    ├── dashboard.html
    ├── workout.html
    └── auth/
        ├── login.html
        └── signup.html
```

---

## Installation & Setup

### Prerequisites

- Python 3.9 – 3.12
- A webcam
- Git

### Steps (Windows)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/fitform-ai.git
cd fitform-ai

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

Then open **http://localhost:5000** in your browser.

> **Note:** The first time you start the app, the SQLite database (`fitness.db`) is created automatically. MediaPipe downloads its pose model on first use — this may take a moment.

**Alternatively**, just double-click `run.bat` — it handles everything automatically.

---

## Usage

1. **Sign up** at `/auth/signup` — provide your name, email, and password
2. After login, you'll land on your **dashboard** showing workout stats and history
3. Navigate to **Start Workout** in the sidebar
4. Select an exercise (Squat, Push-up, or Bicep Curl)
5. Click **Start Camera** — allow webcam access when prompted
6. Stand so your full body is visible in the frame
7. Begin exercising — the app counts reps automatically and shows live feedback
8. Click **Save Session** to record the workout to your history

---

## Screenshots

### Login Page

![Login Page](screenshots/login-page.png)

Clean authentication interface with password strength indicator and dark mode support.

---

### Dashboard

![Dashboard](screenshots/dashboard.png)

Personalized dashboard showing total reps, sessions, calories burned, weekly progress chart, and exercise breakdown.

---

### Workout Detection

![Workout Detection](screenshots/workout-detection.png)

Live webcam feed with MediaPipe skeleton overlay, real-time feedback banner, rep counter, and accuracy ring.

---

### Dark Mode

![Dark Mode](screenshots/dark-mode.png)

Full dark theme — toggled via the toolbar button, persisted across sessions.

---

### Workout History

![Workout History](screenshots/workout-history.png)

Session history table with exercise type, rep count, accuracy score, calories burned, and duration.

---

## Screenshots Folder Guide

To add screenshots to this README, place your image files inside a `screenshots/` folder at the root of the project:

```
ai fitness/
├── screenshots/
│   ├── login-page.png
│   ├── dashboard.png
│   ├── workout-detection.png
│   ├── dark-mode.png
│   └── workout-history.png
```

Capture screenshots from your running local instance at `http://localhost:5000` using your browser's built-in screenshot tool or a tool like Greenshot. Recommended dimensions: **1280 × 800px**.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Yes | Dashboard page |
| GET | `/auth/login` | No | Login page |
| POST | `/auth/login` | No | Process login |
| GET | `/auth/signup` | No | Signup page |
| POST | `/auth/signup` | No | Create account |
| GET | `/auth/logout` | Yes | Logout |
| GET | `/api/stats` | Yes | Aggregate workout stats (JSON) |
| GET | `/api/history` | Yes | Last 20 workout sessions (JSON) |
| GET | `/workout/` | Yes | Workout page |
| POST | `/workout/api/analyze` | Yes | Analyze webcam frame (JSON) |
| POST | `/workout/api/save` | Yes | Save completed session |
| POST | `/workout/api/reset` | Yes | Reset rep counter |

---

## Database Schema

### `users`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Display name |
| email | VARCHAR(150) | Unique, indexed |
| password_hash | VARCHAR(256) | Werkzeug hash |
| created_at | DATETIME | Auto |

### `workout_sessions`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| user_id | INTEGER | FK → users.id |
| exercise_type | VARCHAR(50) | squat / pushup / bicep_curl |
| reps | INTEGER | |
| accuracy_score | FLOAT | 0 – 100 |
| calories_burned | FLOAT | MET estimate |
| duration_seconds | INTEGER | |
| created_at | DATETIME | Indexed |

---

## Future Improvements

- **More exercises** — lunges, shoulder press, pull-ups, plank timer
- **Voice feedback** — spoken form cues via the Web Speech API so you don't need to look at the screen
- **Pose comparison mode** — overlay a reference silhouette alongside your own skeleton
- **AI-based personalization** — adapt thresholds based on the user's own baseline mobility
- **Mobile PWA** — package as a Progressive Web App for phone-based front camera use
- **Export to CSV** — download workout history for external analysis
- **Multi-angle detection** — handle side-on and diagonal camera positions

---

## Contributing

Contributions are welcome. If you find a bug or want to add an exercise, open an issue first to discuss it.

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "Add: description of your change"
git push origin feature/your-feature-name
# Open a pull request
```

Please keep pull requests focused — one feature or fix per PR.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Author

**Dhvani Vaghasiya**

Built as a final year project / portfolio project demonstrating real-time computer vision, full-stack web development, and practical AI integration.

- GitHub: [github.com/dhvanivaghasiya](https://github.com/dhvanivaghasiya)

---

*Built with Python, Flask, MediaPipe, and a lot of squats.*
