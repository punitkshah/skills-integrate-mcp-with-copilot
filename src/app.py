"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import json

################################################################################
# Simple Admin Authentication Layer
# - Loads teacher credentials from teachers.json at startup.
# - Provides /login, /logout, /me endpoints.
# - Protects signup/unregister operations so only authenticated teachers mutate.
# NOTE: This is intentionally lightweight (NO hashing, sessions via signed cookie
# could be added later). For now, stores plain text for simplicity per issue #5.
################################################################################

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory teacher credential store
_teachers_path = current_dir / "teachers.json"
try:
    with open(_teachers_path, "r", encoding="utf-8") as f:
        _teacher_data = json.load(f)
        TEACHERS = {t["username"]: t["password"] for t in _teacher_data.get("teachers", [])}
except FileNotFoundError:
    TEACHERS = {}


def require_teacher(request: Request):
    """Dependency to ensure a logged-in teacher for mutating endpoints."""
    user = request.cookies.get("session_user")
    if not user or user not in TEACHERS:
        raise HTTPException(status_code=401, detail="Teacher login required")
    return user


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, teacher: str = Depends(require_teacher)):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, teacher: str = Depends(require_teacher)):
    """Unregister a student from an activity"""
@app.post("/login")
def login(request: Request, credentials: dict):
    """Authenticate a teacher and set a simple cookie session.

    Expected JSON body: {"username": "...", "password": "..."}
    """
    username = credentials.get("username", "").strip()
    password = credentials.get("password", "")
    if username in TEACHERS and TEACHERS[username] == password:
        resp = {"message": "Login successful", "username": username}
        response = Response(content=json.dumps(resp), media_type="application/json")
        # Basic cookie (NOT secure for production). HttpOnly for minimal protection.
        response.set_cookie("session_user", username, httponly=True, samesite="lax")
        return response
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/logout")
def logout():
    response = Response(content=json.dumps({"message": "Logged out"}), media_type="application/json")
    response.delete_cookie("session_user")
    return response


@app.get("/me")
def me(request: Request):
    user = request.cookies.get("session_user")
    if user and user in TEACHERS:
        return {"authenticated": True, "username": user}
    return {"authenticated": False}

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
