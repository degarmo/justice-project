from datetime import timedelta
from tracker.utils.ai_analysis import analyze_behavior


def analyze_behavior(visitor, behaviors):
    score = 0
    mouse_moves = 0
    clicks = 0
    scroll_changes = 0
    typing_delays = []
    total_events = 0
    session_start = None
    session_end = None

    for behavior in behaviors:
        event = behavior.event_type
        total_events += 1
        timestamp = behavior.timestamp

        if not session_start or timestamp < session_start:
            session_start = timestamp
        if not session_end or timestamp > session_end:
            session_end = timestamp

        if event == "mousemove":
            mouse_moves += 1
        elif event == "click":
            clicks += 1
        elif event == "scroll":
            scroll_changes += 1
        elif event == "keydown":
            typing_delays.append(behavior.data.get("delay", 0))

    session_duration = (session_end - session_start).total_seconds() if session_start and session_end else 0

    # Apply metrics
    if mouse_moves > 200 and session_duration <= 120:
        score += 2
    if clicks > 20 and session_duration <= 120:
        score += 3
    if scroll_changes > 5:
        score += 2
    if any(delay < 30 or delay > 5000 for delay in typing_delays):
        score += 3
    if session_duration < 60 and total_events > 100:
        score += 5

    return score
