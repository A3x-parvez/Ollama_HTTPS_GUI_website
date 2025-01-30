import os
import streamlit as st
import ollama
import subprocess
import time

# Function to start the Ollama server
def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ollama server started successfully.")
    except Exception as e:
        print(f"Error starting Ollama server: {e}")

# Start the Ollama server automatically when the app is run
start_ollama_server()

# Function to load chat history from a local file
def load_chat_history():
    history_file = "chat_history.txt"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return file.readlines()
    return []

# Function to save chat history to a local file
def save_chat_history(user_message, ai_message):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(f"{user_message} **AI:** {ai_message}\n")

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
    st.markdown(
    """<span style ="font-size: 22px;
        font-weight: bold;
        color: #11111; 
        margin-bottom: -20px; ">Settings ⚙️</span>""",
    unsafe_allow_html=True)

    # Model Selection
    st.markdown(
    """<span style ="font-size: 16px;
        font-weight: bold;
        color: #ff5c33; 
        margin-bottom: -20px; ">Select Model🦙:</span>""",
    unsafe_allow_html=True)

    model_list = ollama.list()
    model_names = [model.model for model in model_list.models]
    OLLAMA_MODEL = st.selectbox("", model_names, label_visibility="collapsed")

    # Chat History Section with Scroll
    st.markdown(
    """<span style ="font-size: 16px;
        font-weight: bold;
        color: #ff5c33; 
        margin-bottom: -20px; ">Chat History :</span>""",
    unsafe_allow_html=True)

    # Create a scrollable div for the chat history
    chat_history = load_chat_history()
    if chat_history:
        chat_history_markdown = ""
        for chat in chat_history:
            try:
                # Ensure the message is split correctly (user and AI responses)
                if '**AI:**' in chat:
                    user_message, ai_message = chat.split('**AI:**')
                    user_message = user_message.strip()
                    ai_message = ai_message.strip()

                    # Format the chat history in Markdown format
                    chat_history_markdown +=f"""
                    <div style="max-height: 400px; overflow-y: scroll; border-radius: 5px;">
                     **You:** {user_message}  
                    **AI:** {ai_message}  
                    ---  
                    </div>
                     """
            except Exception as e:
                st.error(f"Error processing chat history: {e}")
        
        # Display chat history in a scrollable container with Markdown
        st.markdown(chat_history_markdown, unsafe_allow_html=True)

    # Clear Chat History Button
    if st.button("🗑 Clear Chat History"):
        open("chat_history.txt", "w", encoding="utf-8").close()
        st.success("✅ Chat History Cleared!")
        st.rerun()  # Refresh UI

# Main Page - Chat Interface
st.markdown("""<span style ="color: red; font-weight: bold; font-size: 49px;">Ollama AI Chatbot 🤖</span>""", unsafe_allow_html=True)

# Chat Input Section
st.markdown(
    """<span style ="font-size: 19px;
        font-weight: bold;
        color: #11111; 
        margin-bottom: -20px; ">Chat with the Model : </span>""",
    unsafe_allow_html=True)
prompt = st.text_area("", placeholder="Type your message here...", label_visibility="collapsed")

# Display last AI response if available
if 'last_response' in st.session_state:
    st.success("AI Response:")
    st.write(st.session_state['last_response'])

# Generate Response Button
if st.button("Generate Response"):
    if prompt.strip():
        with st.spinner("🤔 Thinking..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                bot_response = response["message"]["content"]
                
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
        st.warning("⚠ Please enter a message.")
