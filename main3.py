import os
import streamlit as st
import ollama
import subprocess
import time
from datetime import datetime

# Function to start the Ollama server
def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ollama server started successfully.")
    except Exception as e:
        print(f"Error starting Ollama server: {e}")

# Start the Ollama server automatically when the app is run
start_ollama_server()

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
    filename = os.path.join(CHAT_DIR, f"chat_{topic}_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"👤You : {user_message}\n🤖AI : {ai_message}\n")

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

# Sidebar UI - Chat History & Model Selection
with st.sidebar:
    st.markdown("""<span style ="color: #ff5c33; font-weight: bold; font-size: 28px;">Settings ⚙️</span>""", unsafe_allow_html=True)
    
    # Model Selection
    st.markdown("""<span style ="color: white ; font-weight: bold font-size: 18px;">Select Model🦙:</span>""", unsafe_allow_html=True)
    try:
        model_list = ollama.list()
        model_names = [model.model for model in model_list.models]
        OLLAMA_MODEL = st.selectbox("", model_names, label_visibility="collapsed")
    except Exception as e:
        st.error(f"Error loading models: {e}")
        OLLAMA_MODEL = None
    
    # Chat History Section with List of Chats
    st.markdown("""<span style ="color: blue; font-weight: bold font-size: 18px;">Chat History:</span>""", unsafe_allow_html=True)
    chat_files = get_chat_files()
    selected_chat = st.selectbox("Select a chat", chat_files, index=0 if chat_files else None, label_visibility="collapsed")
    
    if selected_chat:
        chat_content = load_chat_history(selected_chat)
        # st.text_area("Chat History", chat_content, height=300, disabled=True)
        st.markdown(
            f"""
            <div style="max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #00000;">
                {chat_content}
            </div>
            """,
            unsafe_allow_html=True
        )
        # st.markdown(
        # """
        # <div style="max-height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #00000;">
        # """,
        # unsafe_allow_html=True
        # )
        # st.markdown(chat_content)  # Process Markdown separately
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Clear Chat History Button
    if st.button("🗑 Clear Chat History"):
        for file in chat_files:
            os.remove(os.path.join(CHAT_DIR, file))
        st.success("✅ Chat History Cleared!")
        st.rerun()  # Refresh UI

# Main Page - Chat Interface
st.markdown("""<span style ="color: red; font-weight: bold; font-size: 43px;">Ollama AI Chatbot 🤖</span>""", unsafe_allow_html=True)

# Chat Input Section
st.markdown("""<span style ="color: white; font-weight: bold; font-size: 20px;"> Chat with the Model : </span>""", unsafe_allow_html=True)
prompt = st.text_area("", placeholder="Type your message here...", label_visibility="collapsed")

# Display last AI response if available
if 'last_response' in st.session_state:
    st.success("AI Response:")
    st.write(st.session_state['last_response'])

# Generate Response Button
if st.button("Generate Response"):
    if prompt.strip() and OLLAMA_MODEL:
        with st.spinner("🤔 Thinking..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                bot_response = response["message"].get("content", "Error: No response content.")
                
                # Display latest AI response in the main page
                st.success("AI Response:")
                typewriter_effect(bot_response)
                
                # Save chat to history and update session state
                save_chat_history(prompt, bot_response)
                st.session_state['last_response'] = bot_response  # Store last response for display
                
                st.rerun()  # Refresh chat history
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠ Please enter a message and ensure a model is selected.")
