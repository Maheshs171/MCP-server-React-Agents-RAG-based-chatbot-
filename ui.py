# import streamlit as st
# import requests

# st.title("Chat with LangGraph Agent")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# if prompt := st.chat_input("Type your message"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         response = requests.post("http://localhost:8001/chat", json={"content": prompt})
#         assistant_msg = response.json()["response"]
#         st.markdown(assistant_msg)
#         st.session_state.messages.append({"role": "assistant", "content": assistant_msg})





import streamlit as st
import requests
import uuid

st.title("Chat with LangGraph Agent")

# Generate session_id only once per page load
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input and send
if prompt := st.chat_input("Type your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to FastAPI with session_id
    try:
        response = requests.post(
            "http://localhost:8001/chat",
            json={"content": prompt, "session_id": st.session_state.session_id},
            timeout=10
        )
        response.raise_for_status()
        assistant_msg = response.json()["response"]
    except Exception as e:
        assistant_msg = f"⚠️ Error: {e} | Response: {getattr(response, 'text', '')}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_msg)
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
