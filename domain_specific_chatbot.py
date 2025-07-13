import streamlit as st
import requests

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Domain Assistant", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica', sans-serif;
        }
        .stApp {
            background-color: #0a1a2f;
            color: white;
        }
        .block-container {
            padding-top: 1rem !important; /* default is ~6rem */
        }
        .header-container {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: flex-start;
            gap: 30px;
            margin-bottom: 20px;
        }
        .text-form-content {
            width: 60%;
        }
        .select-container {
            max-width: 300px;
            margin-bottom: 10px;
        }
        .side-image {
            width: 35%;
            max-width: 300px;
            max-height: 300px;
            display: flex;
            justify-content: flex-end;
            align-items: flex-start;
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            background-color: white !important;
            color: black !important;
        }
        .stButton button {
            background-color: white;
            color: black;
            font-size: 16px;
            border-radius: 6px;
        }
        .chat-container {
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            gap: 30px;
        }
        .chat-area {
            width: 60%;
        }
        .chat-box {
            background-color: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 10px;
            border-left: 5px solid #4b8ef2;
        }
        .user-msg {
            color: #8ecfff;
        }
        .bot-msg {
            color: #ffffff;
        }
        h1, h3 {
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model' not in st.session_state:
    st.session_state.model = None

if 'domain' not in st.session_state:
    st.session_state.domain = None

if st.session_state.model is None or st.session_state.domain is None:
# ------------------ FORM + IMAGE SECTION ------------------
    st.markdown("## Domain-Specific AI Assistant")
    st.markdown("Ask questions related to the chosen domain. Off-topic questions will be declined politely.")
    st.markdown("---")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        with st.form(key="model_form"):
            st.selectbox("Select Model", ["tinyllama", "phi", "qwen3:0.6b"], index=0, key="model_select")
            st.selectbox("Select Domain", ["Medical", "Science", "IT", "Art"], index=0, key="domain_select")
            start_clicked = st.form_submit_button("Start Chat")

    with right_col:
        st.image("image1.png", use_container_width=True)

    if start_clicked:
        st.session_state.model = st.session_state.model_select
        st.session_state.domain = st.session_state.domain_select
 
else:
    st.markdown(f"**Model:** `{st.session_state.model}` | **Domain:** `{st.session_state.domain}`")
    st.divider()

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)

    for role, msg in st.session_state.chat_history:
        msg_class = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f"<div class='chat-box {msg_class}'><strong>{role.capitalize()}:</strong> {msg}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Type your message", key="user_message")

    if st.button("Send") and user_input.strip():
        model = st.session_state.model
        domain = st.session_state.domain

        # Generate prompt based on selected model
        if model == "tinyllama":
            prompt = f"""
        You are a domain-specific AI assistant. Only answer questions that are related to the domain: {domain}.

        Instructions:
        - Only answer questions if they are related to the domain of {domain}.
        - If the question is not clearly related to {domain}, politely decline.
        - If the question is relevant, provide a short and factual response.
        Question: {user_input}
        Answer:"""
        elif model == "phi":
            prompt = f"""
        Act as an expert assistant that only answers {domain} questions.
        Politely decline any question not related to {domain} with:
        "Sorry, I can only answer questions related to {domain}."

        Question: {user_input}
        Answer:"""
        elif model == "qwen3:0.6b":
            prompt = f"""
        You are a domain-specific assistant restricted to the topic: {domain}.
        Instructions:
        - Respond to relevant queries.
        - If the query is NOT about {domain}, say: "Sorry, I can only answer questions related to {domain}."

        User: {user_input}
Assistant:"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            data = response.json()
            bot_reply = data.get("response", "⚠️ No valid response from model.")
        except Exception as e:
            bot_reply = f"⚠️ Error: {str(e)}"

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", bot_reply))
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ RESET BUTTON ------------------
    if st.button("Change Model or Domain"):
        st.session_state.model = None
        st.session_state.domain = None
        st.session_state.chat_history = []
        st.rerun()
