import streamlit as st
from db.models import init_db

# Create database tables on startup (safe to call every time)
init_db()

# Set default values in session_state if not already set
# session_state stores values that persist across page reruns
defaults = {
    'logged_in': False,    # is the user logged in?
    'user_id':   None,     # database id of logged-in user
    'username':  None,     # username of logged-in user
    'name':      None,     # full name of logged-in user
    'profile':   None,     # investor profile dict
    'plan':      None,     # generated investment plan dict
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.set_page_config(
    page_title = "KashGroww",
    page_icon  = "💸",
    layout     = "wide"
)

st.title("💸📈KashGroww — Robo-Advisory Platform")
st.header("Customise your Cash, Master  your Growth!🚀✅ ")
st.subheader("Get Personalised Investment Planning")

if st.session_state['logged_in']:
    st.success(f"Welcome back, {st.session_state['name']}!")
    st.page_link("pages/2_Profile.py", label="→ Go to your investor profile")
else:
    st.info("Please sign in to continue.")
    st.page_link("pages/1_Login.py", label="→ Sign in or Register")