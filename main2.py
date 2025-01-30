import streamlit as st
import ollama
import subprocess

def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ollama server started successfully.")
    except Exception as e:
        print(f"Error starting Ollama server: {e}")
    
    
# Start the Ollama server
start_ollama_server()

# Set page config before any other Streamlit command
st.set_page_config(page_title="Ollama AI Chat", layout="centered")
# st.title("🦙 Ollama AI Chatbot ")
st.markdown("""<span style =" color : red; font-weight: bold; font-size: 49px;">Ollama AI Chatbot 🤖</span>""", unsafe_allow_html=True)
# Select the model from a dropdown

st.markdown(
    """<span style ="font-size: 18px;
        font-weight: bold;
        color: #ff5c33; 
        margin-bottom: -20px; ">Select the LLM Model :</span>""",
    unsafe_allow_html=True)

model_list = ollama.list()
model_names = tuple(model.model for model in model_list.models)

model = st.selectbox(
    '',
    # ('llama3.2:1b', 'phi3', 'gemma2:2b'), 
    model_names,
    label_visibility="collapsed"
)

# Define the model
OLLAMA_MODEL = model

# Streamlit UI
# st.write("Enter a prompt and get a response from the model.")
st.markdown(
    """<span style ="font-size: 18px;
        font-weight: bold;
        color: #ff5c33; 
        margin-bottom: -20px; ">Chat with the Model : </span>""",
    unsafe_allow_html=True)

# Input field for the prompt
prompt = st.text_area("", placeholder="Type your message here...",label_visibility="collapsed")

# Generate response on button click
if st.button("Generate Response"):
    if prompt.strip():
        with st.spinner("Generating response..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                st.success("Here is the Ans : ")
                st.write(response["message"]["content"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid prompt.")
