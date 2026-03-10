import streamlit as st
from datetime import datetime, timedelta, date

st.set_page_config(
    page_title="Schengen 90/180 Tracker",
    page_icon="🛂",
    layout="centered"
)

MAX_DAYS = 90
WINDOW_DAYS = 180

# -----------------------------
# Core Logic
# -----------------------------

def days_in_window(trips, reference_date):
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
                errors.append(f"Trip {i+1} overlaps with trip {i}. Please fix the dates.")

    return errors, sorted_trips


def next_breach_date(trips, start_date=None):
    if start_date is None:
        start_date = date.today()

    current = start_date
    for _ in range(365):
        used = days_in_window(trips + [(start_date, current)], current)
        if used > MAX_DAYS:
            return current
        current += timedelta(days=1)
    return None


# -----------------------------
# Premium Header
# -----------------------------

st.markdown(
    """
    <div style='text-align: center; margin-top: 10px;'>
        <h1 style='margin-bottom: 0;'>🛂 Schengen 90/180 Tracker</h1>
        <p style='color: #888; margin-top: 0; font-size: 1.1rem;'>
            A clean and accurate way to calculate your Schengen allowance
        </p>
    </div>
    <hr style='margin-top: 10px; margin-bottom: 30px;'>
    """,
    unsafe_allow_html=True
)

st.info("Entry and exit days both count as Schengen days.")

# -----------------------------
# Trip Controls
# -----------------------------

if "rows" not in st.session_state:
    st.session_state.rows = 1

control_col1, control_col2 = st.columns([1, 1])

with control_col1:
    if st.button("➕ Add trip"):
        st.session_state.rows += 1

with control_col2:
    if st.button("➖ Remove trip") and st.session_state.rows > 1:
        st.session_state.rows -= 1

# -----------------------------
# Trip Input Form
# -----------------------------

trips = []

with st.form("trip_form"):
    st.markdown(
        "<h3 style='margin-bottom: 10px;'>Your Trips</h3>",
        unsafe_allow_html=True
    )

    for i in range(st.session_state.rows):
        st.markdown(
            f"""
            <div style='margin-top: 20px; padding: 15px; border: 1px solid #444; border-radius: 8px;'>
                <h4 style='margin-top: 0;'>Trip {i+1}</h4>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            entry = st.date_input(
                "Entry date",
                key=f"entry_{i}",
                value=date.today() - timedelta(days=7) if i == 0 else date.today(),
                format="DD/MM/YYYY"
            )

        with col2:
            exit_ = st.date_input(
                "Exit date",
                key=f"exit_{i}",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        trips.append((entry, exit_))

        st.markdown("</div>", unsafe_allow_html=True)

    reference_date = st.date_input("Check allowance on date", value=date.today())
    submitted = st.form_submit_button("Calculate", use_container_width=True)

# -----------------------------
# Results Section
# -----------------------------

if submitted:
    errors, trips = validate_trips(trips)

    if errors:
        for err in errors:
            st.error(err)

    else:
        used_days = days_in_window(trips, reference_date)
        remaining_days = MAX_DAYS - used_days

        st.markdown(
            """
            <div style='padding: 20px; border: 1px solid #444; border-radius: 8px; margin-top: 20px;'>
            """,
            unsafe_allow_html=True
        )

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
                st.write(f"Trip {idx}: {entry} → {exit_} ({duration} days)")

        breach = next_breach_date(sorted_trips, start_date=reference_date)
        if breach:
            safe_last_day = breach - timedelta(days=1)
            st.write(f"Last legal day if staying continuously: **{safe_last_day}**")
            st.write(f"You would exceed the limit on **{breach}**.")

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------

st.markdown(
    """
    <div style='text-align: center; margin-top: 40px; padding-top: 20px; 
                color: #888; font-size: 0.85rem; border-top: 1px solid #444;'>
        © 2026 New Image Designs
    </div>
    """,
    unsafe_allow_html=True
)
