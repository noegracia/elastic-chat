import streamlit as st
import chat
import search_query as sq


st.title("Elastic Chat LLM Demo")

# Main chat form
with st.form("chat_form"):
    query = st.text_input("You: ")
    submit_button = st.form_submit_button("Send")
    clear_button = st.form_submit_button("Clear Chat")

# Generate and display response on form submission
if submit_button:
    resp, url = sq.search(query)
    
    prompt = f"Answer this question: {query}\nUsing only the information from this Elastic Doc: {resp}\nIf the answer is not contained in the supplied doc reply '{chat.negResponse}' and nothing else"
    
    answer = chat.chat_gpt(prompt)
    
    if chat.negResponse in answer:
        st.write(f"ChatGPT: {answer}")
    else:
        st.write(f"ChatGPT: {answer}\n\nDocs: {url}")