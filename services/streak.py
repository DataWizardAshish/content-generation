"""
STREAK LOGIC — GENTLE / PARENT-FRIENDLY
========================================
- weekly_active_days = unique days active in last 7 calendar days
- current_streak_days = consecutive days active up to today
- GRACE DAY: 1 missed day does NOT break the streak
  (streak breaks only if 2+ consecutive days missed)
- Streak never silently decremented in background —
  only recalculated on next user action (POST /user-progress/answer)
- UI copy: "4 of 7 days this week" not "X day streak 🔥"
"""
import datetime


def calculate_streak(last_active_date: datetime.date | None, current_streak: int) -> int:
    """
    Returns new streak value based on last active date and existing streak.
    Grace day: 1 missed day keeps streak, 2+ missed days resets to 1.
    """
    today = datetime.date.today()

    if last_active_date is None:
        return 1

    if last_active_date == today:
        return current_streak

    days_since = (today - last_active_date).days

    if days_since == 1:
        # Active yesterday — streak continues
        return current_streak + 1
    elif days_since == 2:
        # Missed exactly one day — grace day, streak holds (don't increment though)
        return current_streak
    else:
        # Missed 2+ days — streak resets
        return 1


def calculate_weekly_active(activity_dates: list[datetime.date]) -> int:
    """Count unique days active in the last 7 calendar days (including today)."""
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=6)
    recent = {d for d in activity_dates if cutoff <= d <= today}
    return len(recent)


def week_summary_copy(weekly_active_days: int) -> str:
    return f"{weekly_active_days} of 7 days this week"
