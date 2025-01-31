import os
import streamlit as st
import ollama
import subprocess
import time
from datetime import datetime
import re

# Set Streamlit page configuration - Must be at the very top
st.set_page_config(page_title="Ollama-AI-v5", layout="wide")

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


# Directory for saving chat history
CHAT_DIR = "chat_history"
os.makedirs(CHAT_DIR, exist_ok=True)

# Function to get list of chat files
def get_chat_files():
    return sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".txt")], reverse=True)

# Function to save chat history to a separate file
def save_chat_history(user_message, ai_message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    topic = user_message[:30].replace(" ", "_") if user_message else "General_Chat"
     # Sanitize the topic part of the filename to avoid invalid characters
    sanitized_topic = re.sub(r'[\\/*?:"<>|\n]', "_", topic)  # Replace invalid characters with '_'
    
    filename = os.path.join(CHAT_DIR, f"chat_{sanitized_topic}_{timestamp}.txt")
    # filename = os.path.join(CHAT_DIR, f"chat_{topic}_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as file:
        # file.write(f"👤You : {user_message}<br>🤖AI : {ai_message}\n")
        file.write(f"<html><body><span style='font-size:19px; color: #ff5c33; font-weight: bold;'>👤You :</span><br>{user_message}<br><span style='font-size:19px; color: #ff5c33; font-weight: bold;'>🤖AI :</span><br>{ai_message}<br></body></html>")

# Function to load a specific chat file
def load_chat_history(filename):
    file_path = os.path.join(CHAT_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return ""

# Typewriter effect for displaying AI response
def typewriter_effect(text):
    message = st.empty()
    output = ""
    for char in text:
        output += char
        message.markdown(f"<span style='font-size:16px;'>{output}</span>", unsafe_allow_html=True)
        time.sleep(0.002)  # Adjust speed for smooth effect

# Sidebar UI - Install Model & Model Selection
with st.sidebar:
    st.markdown("""<span style ="color: #white; font-weight: bold; font-size: 38px;">Settings ⚙️</span>""", unsafe_allow_html=True)
    
    # Model Installation Section at the top
    st.markdown("""<span style ="color: #ff5c33; font-weight: bold; font-size: 22px;">Install Model 🛠️</span>""", unsafe_allow_html=True)
    new_model = st.text_input("",placeholder="Enter model name to install:",label_visibility="collapsed")
    install_progress = st.empty()  # Progress bar container

    if st.button("Install Model",use_container_width=True):
        if new_model.strip():
            try:
                install_progress.progress(0)  # Initialize the progress bar
                st.write(f"Installing model '{new_model.strip()}'... Please wait.")
                
                # Run the model installation with subprocess
                result = subprocess.run(
                    ["ollama", "pull", new_model.strip()],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                
                # Check for the result and handle success
                if result.returncode == 0:
                    st.success(f"✅ Model '{new_model.strip()}' installed successfully!")
                    install_progress.progress(100)  # Complete the progress bar
                    st.rerun()  # Refresh the UI after install
                else:
                    st.error(f"Error installing model: {result.stderr}")
                    install_progress.progress(0)  # Reset progress bar on error
                    st.rerun()
            except Exception as e:
                st.error(f"Error installing model: {e}")
                install_progress.progress(0)  # Reset progress bar on exception
                st.rerun()
    
    # Model Selection Section
    st.markdown("""<span style ="color: #ff5c33; font-weight: bold; font-size: 22px;">Select Model🦙</span>""", unsafe_allow_html=True)
    try:
        model_list = ollama.list()
        model_names = [model.model for model in model_list.models]
        OLLAMA_MODEL = st.selectbox("", model_names, label_visibility="collapsed",key="chat")
    except Exception as e:
        st.error(f"Error loading models: {e}")
        OLLAMA_MODEL = None

    # Model Management Section for Deleting Models
    st.markdown("""<span style ="color: #ff5c33; font-weight: bold; font-size: 22px;">Delete Model ⚠️</span>""", unsafe_allow_html=True)
    delete_model = st.selectbox("", model_names, label_visibility="collapsed",key="del")
    if st.button("Delete Model",use_container_width=True):
        
        if st.button("yes i want to delete",use_container_width=True):
            try:
                subprocess.run(["ollama", "rm", delete_model], check=True)
                st.success(f"✅ Model '{delete_model}' deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting model: {e}")
                st.rerun()
        if st.button("No i don't want to delete",use_container_width=True):
            st.warning("Model deletion cancelled.")
            st.rerun()

    # Chat History Section with List of Chats
    st.markdown("""<span style ="color: #ff5c33; font-weight: bold; font-size: 22px;">Chat History 💬</span>""", unsafe_allow_html=True)
    chat_files = get_chat_files()
    selected_chat = st.selectbox("Select a chat", chat_files, index=0 if chat_files else None, label_visibility="collapsed")
    
    if selected_chat:
        chat_content = load_chat_history(selected_chat)
        st.markdown(
            f"""
            <div style="max-height: 400px; overflow-y: auto; padding: 10px; border: 2px solid #ddd; border-radius: 10px; background-color: #00000;">
            {chat_content}</div>
            """,
            unsafe_allow_html=True
        )
        # st.markdown(f"""{chat_content}""", unsafe_allow_html=True)
        # st.markdown("</div>", unsafe_allow_html=True)
    
    # Clear Chat History Button
    if st.button("Clear Chat History 🗑 ",use_container_width=True):
        for file in chat_files:
            os.remove(os.path.join(CHAT_DIR, file))
        st.success("✅ Chat History Cleared!")
        st.rerun()  # Refresh UI

# Main Page - Chat Interface
st.markdown("""<span style ="color: red; font-weight: bold; font-size: 43px;">Ollama AI Chatbot 🤖</span>""", unsafe_allow_html=True)

# Chat Input Section
st.markdown("""<span style ="color: white; font-weight: bold; font-size: 20px;"> Chat with the Model : </span>""", unsafe_allow_html=True)
prompt = st.text_area("", placeholder="Type your message here...", label_visibility="collapsed")

# Generate Response Button
if st.button("Generate Response"):
    if prompt.strip():
        with st.spinner("🤔 Thinking..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                bot_response = response["message"]["content"]
                
                # Display latest AI response in the main page
                st.success("Here is your ans :")
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
    st.success("Here is your ans :")
    st.write(st.session_state['last_response'])
