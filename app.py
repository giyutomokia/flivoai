from flask import Flask, request, jsonify
import google.generativeai as genai
import logging
import justiceAI_prompt as jp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# User-specific details
ai_name = "Flivo AI"

# Configure API key
api_key = "AIzaSyDgc78PnoUQUau0m4QbAUJtYIv9BKNbHhU"
genai.configure(api_key=api_key)

# Initialize the model outside of the function
model = genai.GenerativeModel('gemini-pro')

# Initialize conversation history log
conversation_log = []


def summarize_response(ai_response):
    """Summarizes AI responses to less than 100 characters."""
    summary_prompt = f"""
    Please summarize the following response in less than 100 characters:
    "{ai_response}"
    """
    try:
        summary_response = model.generate_content(summary_prompt)
        return summary_response.text.strip()
    except Exception as e:
        logging.error(f"Error summarizing response: {e}")
        return "Summary could not be generated."


def save_conversation(question, ai_response):
    """Saves the conversation by summarizing and logging it."""
    summarized_response = summarize_response(ai_response)
    conversation_log.append({'question': question, 'response_summary': summarized_response})


def generate_prompt(Question_input):
    """Generates the prompt for the AI model."""
    summary = "\n".join(
        [f"User asked: '{log['question']}', AI responded: '{log['response_summary']}'"
         for log in conversation_log]
    ) if conversation_log else "No previous conversation history yet."

    # Instruct the model to generate a detailed response
    instruction = "\nPlease provide a detailed and coherent response of approximately 1000 words."

    prompt = jp.prompt + "\nNow the question is: " + Question_input + "\nAnd the previous conversation was this: " + summary + instruction
    return prompt


def generate_ai_response(prompt):
    """Generates a detailed response from the AI."""
    try:
        # Using the default parameters for content generation
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return f"An error occurred: {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles user input and generates responses."""
    if request.method == 'POST':
        user_input = request.form['user_input'].strip()

        if user_input.lower() == "exit":
            return jsonify({'ai_name': ai_name, 'response': "Goodbye!", 'conversation_log': conversation_log})

        if not user_input:
            return jsonify({'response': "Input cannot be empty. Please try again."})

        question = generate_prompt(user_input)

        if not question.strip():
            return jsonify({'response': "Generated prompt is empty. Please check your input."})

        logging.debug(f"Generated Question: {question}")

        response = generate_ai_response(question)
        save_conversation(user_input, response)

        return jsonify({'ai_name': ai_name, 'response': response, 'conversation_log': conversation_log})

    return '''
        <html>
        <head>
            <title>Flivo AI Interface</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #f7f7f7;
                    color: #333;
                }
                h1 {
                    text-align: center;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                input[type="text"] {
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    font-size: 16px;
                }
                .response {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #e9e9e9;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                #response-section {
                    display: none;
                }
            </style>
            <script>
                function sendRequest() {
                    var userInput = document.getElementById("user_input").value;
                    var responseSection = document.getElementById("response-section");
                    var formData = new FormData();
                    formData.append("user_input", userInput);

                    fetch("/", {
                        method: "POST",
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("ai_response").innerText = data.response;
                        responseSection.style.display = "block";
                    })
                    .catch(error => {
                        console.error("Error:", error);
                    });
                }
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Ask a Question to Flivo.AI</h1>
                <form onsubmit="event.preventDefault(); sendRequest();">
                    <label for="user_input">Enter your question:</label><br>
                    <input type="text" id="user_input" name="user_input" required><br><br>
                    <input type="submit" value="Submit">
                </form>
                <div id="response-section" class="response">
                    <strong>AI Response:</strong>
                    <p id="ai_response"></p>
                </div>
            </div>
        </body>
        </html>
    '''


if __name__ == '__main__':
    app.run(debug=True)
