import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],  # Use Streamlit secrets for API key
)

# Streamlit app
st.title("Software Development Query AI")

# Input for the type of software to be built
software_type = st.text_input("What type of software are you building?", placeholder="e.g., web app, mobile app, AI system")

# Input for key points about the software
key_points = st.text_area("What are the key points about the software?", placeholder="e.g., user authentication, real-time updates, scalable")

# Function to generate questions
def generate_questions(software_type, key_points):
    prompt = f"""
    You are an expert software development AI assisting a developer. The user is building a "{software_type}" software with these key points:  
    "{key_points}"  

    Generate exactly 5 concise, relevant, and diverse questions to gather critical details about the software. Focus on:  
    1. Functional requirements (what it does).  
    2. Technical constraints (e.g., platform, performance).  
    3. Target users or stakeholders.  
    4. Development timeline or scope.  
    5. Integration or compatibility needs.  

    Return only the questions, one per line, with no additional text, explanations, or numbering. Ensure each question ends with a question mark.
    """
    completion = client.chat.completions.create(
     
        model="meta-llama/llama-3.2-1b-instruct:free",  # Use the desired model
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Function to clean and extract questions from the response
def extract_questions(response):
    # Split the response into lines and filter out empty lines or non-question lines
    lines = response.split('\n')
    questions = [line.strip() for line in lines if line.strip() and line.strip().endswith('?')]
    # Ensure exactly 5 questions, adding fallback if needed
    if len(questions) < 5:
        questions.extend([f"What additional details can you provide about {software_type}?" for _ in range(5 - len(questions))])
    return questions[:5]

# Function to generate response
def generate_response(software_type, key_points, combined_answers):
    prompt = f"""
    You are an expert software development AI advising a developer. The user is building a "{software_type}" software with these key points:  
    "{key_points}"  

    Based on the following Q&A from the user:  
    "{combined_answers}"  

    Provide a detailed, structured response on how to approach building this software. Include:  
    1. Recommended methodology (e.g., Agile, Waterfall) with a brief rationale.  
    2. Key development phases and best practices for each (e.g., planning, coding, testing).  
    3. Suggested tools or technologies based on the input.  
    4. Potential challenges and mitigation strategies.  

    Structure your response with clear section headers (e.g., "Methodology", "Development Phases"). Keep it actionable, concise, and tailored to the user's input. Avoid generic filler content.
    """
    completion = client.chat.completions.create(
        
        model="meta-llama/llama-3.2-1b-instruct:free",  # Use the desired model
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Button to generate questions
if st.button("Generate Questions"):
    if software_type and key_points:
        questions_response = generate_questions(software_type, key_points)
        questions = extract_questions(questions_response)
        st.session_state['questions'] = questions
        st.success("Questions generated successfully!")
        st.write("Here are 5 questions to help gather more information:")
        for i, question in enumerate(questions):
            st.write(f"Q{i+1}: {question}")
    else:
        st.error("Please provide both the type of software and key points.")

# Display questions and allow user to answer them
if 'questions' in st.session_state:
    st.subheader("Answer the Questions")
    answers = []
    for i, question in enumerate(st.session_state['questions']):
        answer = st.text_area(f"Q{i+1}: {question}", key=f"q{i}", placeholder="Your answer here...")
        answers.append(answer)

    # Button to generate a response based on the answers
    if st.button("Generate Response"):
        if all(answers):  # Ensure all questions are answered
            combined_answers = "\n".join([f"Q{i+1}: {question}\nA{i+1}: {answer}" for i, (question, answer) in enumerate(zip(st.session_state['questions'], answers))])
            response = generate_response(software_type, key_points, combined_answers)
            st.success("Response generated successfully!")
            st.write("Here is a detailed response on how to approach building this software:")
            st.markdown(response)  # Use markdown for better formatting
        else:
            st.error("Please answer all the questions before generating the response.")

# Footer
st.markdown("---")
