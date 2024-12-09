import google.generativeai as genai
import streamlit as st
import justiceAI_prompt as jp
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# User-specific details
ai_name = "Flivo ai"

# Configure API key
test_string = st.secrets["AIzaSyDgc78PnoUQUau0m4QbAUJtYIv9BKNbHhU"] 
genai.configure(api_key=test_string)

# Initialize the model outside of the function
model = genai.GenerativeModel('gemini-pro')

# Initialize conversation history log
conversation_log = []

def summarize_response(ai_response):
    summary_prompt = f"""
    Please summarize the following response in less than 100 characters:
    "{ai_response}"
    """
    try:
        summary_response = model.generate_content(summary_prompt)
        return summary_response.text.strip()
    except Exception as e:
        st.error(f"Error summarizing response: {e}")
        return "Summary could not be generated."

def save_conversation(question, ai_response):
    summarized_response = summarize_response(ai_response)
    conversation_log.append({'question': question, 'response_summary': summarized_response})

def generate_prompt(Question_input):
    summary = "\n".join([f"User asked: '{log['question']}', AI responded: '{log['response_summary']}'" 
                         for log in conversation_log]) if conversation_log else "No previous conversation history yet."
    prompt = jp.prompt + "\n now the question is " + Question_input + "\n and the previous conversation was this " + summary
    return prompt

# Streamlit UI
st.title(f"Chat with {ai_name}")

user_input = st.text_input("Enter your question", "")

if user_input:
    Question = generate_prompt(user_input)

    if not Question.strip():
        st.error("Generated prompt is empty. Please check your input.")
    else:
        logging.debug(f"Generated Question: {Question}")
        with st.spinner(f"{ai_name} is thinking..."):
            try:
                response = model.generate_content(Question)
                st.write(f"**{ai_name}:** {response.text}")
                save_conversation(user_input, response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
