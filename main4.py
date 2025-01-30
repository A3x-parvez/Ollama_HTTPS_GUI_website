import streamlit as st
import ollama
import subprocess
import os
import time

# Set Streamlit page configuration - Must be at the very top
st.set_page_config(page_title="Ollama AI Chat", layout="wide")

# Automatically start Ollama server
def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.toast("🚀 Ollama server starting...", icon="⚡")
        time.sleep(2)
        # st.success("✅ Ollama Server Started!")
    except Exception as e:
        st.error(f"Error starting Ollama server: {e}")

# Start the server if it hasn't been started
if 'server_started' not in st.session_state:
    start_ollama_server()
    st.session_state['server_started'] = True

# Function to save chat history (UTF-8 to fix encoding issues)
def save_chat_history(user_msg, bot_msg):
    history_file = "chat_history.txt"
    history = load_chat_history()
    new_entry = f"🧑‍💻 **You:** {user_msg}\n🤖 **AI:** {bot_msg}\n\n"
    history.insert(0, new_entry)  # New messages at the top
    with open(history_file, "w", encoding="utf-8") as file:
        file.writelines(history)

# Function to load chat history
def load_chat_history():
    history_file = "chat_history.txt"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return file.readlines()
    return []

# Typewriter effect for displaying AI response
def typewriter_effect(text):
    message = st.empty()
    output = ""
    for char in text:
        output += char
        message.markdown(f"<span style='font-size:16px;'>{output}</span>", unsafe_allow_html=True)
        time.sleep(0.002)  # Adjust speed for smooth effect

# Sidebar UI - Chat History & Model Selection
with st.sidebar:
    st.title("Settings ⚙️")
    
    # Model Selection
    st.subheader("🦙 Select Model:")
    model_list = ollama.list()
    model_names = [model.model for model in model_list.models]
    OLLAMA_MODEL = st.selectbox("", model_names, label_visibility="collapsed")

    # Chat History Section with Scroll
    st.subheader("📜 Chat History")
    chat_history = load_chat_history()
    if chat_history:
        for chat in chat_history:
            st.markdown(chat.strip())

    # Clear Chat History Button
    if st.button("🗑 Clear Chat History"):
        open("chat_history.txt", "w", encoding="utf-8").close()
        st.success("✅ Chat History Cleared!")
        st.rerun()  # Refresh UI

# Main Page - Chat Interface
st.markdown("""<span style ="color: red; font-weight: bold; font-size: 49px;">Ollama AI Chatbot 🤖</span>""", unsafe_allow_html=True)

# Chat Input Section
st.subheader("💬 Chat with the Model")
prompt = st.text_area("", placeholder="Type your message here...", label_visibility="collapsed")

# Generate Response Button
if st.button("Generate Response"):
    if prompt.strip():
        with st.spinner("🤔 Thinking..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                bot_response = response["message"]["content"]
                
                # Display latest AI response in the main page
                st.success("✅ AI Response:")
                typewriter_effect(bot_response)
                
                # Save chat to history and update session state
                save_chat_history(prompt, bot_response)
                st.session_state['last_response'] = bot_response  # Store last response for display
                
                st.rerun()  # Refresh chat history
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠ Please enter a message.")

# Display last AI response if available
if 'last_response' in st.session_state:
    st.write("AI Response:")
    st.write(st.session_state['last_response'])
