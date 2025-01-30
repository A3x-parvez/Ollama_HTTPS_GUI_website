import streamlit as st
import ollama

# Define the model
OLLAMA_MODEL = "llama3.2:1b"  # Change to your preferred Ollama model

st.set_page_config(page_title="Ollama AI Chat", layout="centered")
st.title("🔮 Ollama AI Chatbot")
st.write("Enter a prompt and get a response from the model.")

prompt = st.text_area("Your Prompt", placeholder="Type your message here...")

if st.button("Generate Response"):
    if prompt.strip():
        with st.spinner("Generating response..."):
            try:
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                st.success("Response:")
                st.write(response["message"]["content"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid prompt.")

if __name__ == "__main__":
    st.write("")
