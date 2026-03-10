import streamlit as st
from datetime import datetime, timedelta, date

st.set_page_config(page_title="Schengen 90/180 Tracker", page_icon="🛂", layout="centered")

MAX_DAYS = 90
WINDOW_DAYS = 180


def parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_in_window(trips, reference_date):
    """
    Count Schengen days used in the rolling 180-day window ending on reference_date.
    Assumes both entry and exit dates count as days in Schengen.
    """
    window_start = reference_date - timedelta(days=WINDOW_DAYS - 1)
    total = 0

    for entry, exit_ in trips:
        overlap_start = max(entry, window_start)
        overlap_end = min(exit_, reference_date)
        if overlap_start <= overlap_end:
            total += (overlap_end - overlap_start).days + 1

    return total


def validate_trips(trips):
    errors = []
    sorted_trips = sorted(trips, key=lambda x: x[0])

    for i, (entry, exit_) in enumerate(sorted_trips):
        if exit_ < entry:
            errors.append(f"Trip {i+1}: exit date cannot be before entry date.")
        if i > 0:
            prev_entry, prev_exit = sorted_trips[i - 1]
            if entry <= prev_exit:
                errors.append(
                    f"Trip {i+1} overlaps with trip {i}. Please fix the dates."
                )

    return errors, sorted_trips


def next_breach_date(trips, start_date=None):
    """
    Returns the first date on which the user would exceed 90 days
    if they entered/stayed continuously from start_date onwards.
    """
    if start_date is None:
        start_date = date.today()

    current = start_date
    for _ in range(365):  # enough for planning ahead
        used = days_in_window(trips + [(start_date, current)], current)
        if used > MAX_DAYS:
            return current
        current += timedelta(days=1)
    return None


st.title("🛂 Schengen 90/180 Tracker")
st.write(
    "Add your Schengen trips below. This app calculates how many days you have used "
    "in the rolling 180-day window and how many you have left."
)

st.info("For Schengen counting, entry and exit days are both counted.")

if "rows" not in st.session_state:
    st.session_state.rows = 1

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add trip"):
        st.session_state.rows += 1
with col2:
    if st.button("➖ Remove trip") and st.session_state.rows > 1:
        st.session_state.rows -= 1

trips = []

with st.form("trip_form"):
    for i in range(st.session_state.rows):
        st.subheader(f"Trip {i+1}")
        c1, c2 = st.columns(2)
        with c1:
            entry = st.date_input(
                f"Entry date {i+1}",
                key=f"entry_{i}",
                value=date.today() - timedelta(days=7) if i == 0 else date.today(),
                format="DD/MM/YYYY"
            )
        with c2:
            exit_ = st.date_input(
                f"Exit date {i+1}",
                key=f"exit_{i}",
                value=date.today() if i == 0 else date.today(),
                format="DD/MM/YYYY"
            )
        trips.append((entry, exit_))

    reference_date = st.date_input("Check allowance on date", value=date.today())
    submitted = st.form_submit_button("Calculate")

if submitted:
    errors, trips = validate_trips(trips)

    if errors:
        for err in errors:
            st.error(err)
    else:
        used_days = days_in_window(trips, reference_date)
        remaining_days = MAX_DAYS - used_days

        st.success(f"Days used in the last 180 days: {used_days}")
        st.write(f"Days remaining: **{remaining_days}**")

        if remaining_days < 0:
            st.error("You have exceeded the 90-day allowance.")
        elif remaining_days == 0:
            st.warning("You have no Schengen days remaining on this date.")
        else:
            st.info(f"You can still spend {remaining_days} day(s) in Schengen on {reference_date}.")

        sorted_trips = sorted(trips, key=lambda x: x[0])
        with st.expander("See trip summary"):
            for idx, (entry, exit_) in enumerate(sorted_trips, start=1):
                duration = (exit_ - entry).days + 1
                st.write(f"Trip {idx}: {entry} to {exit_} ({duration} day(s))")

        breach = next_breach_date(sorted_trips, start_date=reference_date)
        if breach:
            safe_last_day = breach - timedelta(days=1)
            st.write(f"If you entered/stayed continuously from **{reference_date}**, your last legal day would be **{safe_last_day}**.")
            st.write(f"You would exceed the limit on **{breach}**.")
