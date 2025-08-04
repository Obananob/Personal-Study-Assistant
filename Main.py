import streamlit as st
import requests
import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from crewai import LLM
import litellm
litellm.set_verbose = true
import sys
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    print("pysqlite3 not available — falling back to default sqlite3")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
gemini_llm = LLM(
    provider = "gemini",
    model = "gemini/gemini-2.0-flash",
    api_key = GEMINI_API_KEY
)
# Inject custom fonts and styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    .flashcard, .quiz, .chat-bubble {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Gemini tool
# class GeminiTool(BaseTool):
#     name: str = "Gemini Tool"
#     description: str = "Generates content using Gemini API"

#     def _run(self, prompt: str) -> str:
#         url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {GEMINI_API_KEY}"
#         }
#         data = {
#             "contents": [{"parts": [{"text": prompt}]}]
#         }
#         response = requests.post(url, headers=headers, json=data)
#         result = response.json()
#         try:
#             return result['candidates'][0]['content']['parts'][0]['text']
#         except:
#             return "Error generating response."
        
# gemini_tool = GeminiTool()

# Sidebar navigation
st.sidebar.title("📚 AI Study Assistant")
page = st.sidebar.radio("Navigate", ["Home", "Note Summarizer", "Flashcards", "Quiz Master", "Tutor Chat"])


# Page routing
if page == "Home":
    st.title("🏠 Welcome to Your Personal Study Assistant")
    st.write("Use the sidebar to explore each module.")
    st.markdown("Built with CrewAI, Gemini, and Streamlit")

elif page == "Note Summarizer":
    st.title("📝 Note Summarizer")
    note = st.text_area("Paste your notes here:")
    if st.button("Summarize"):
        summarizer = Agent(
            role="Note Summarizer",
            goal="Summarize notes into key concepts",
            backstory="An academic expert in summarization",
            #tools=[gemini_tool],
            llm = gemini_llm,
            verbose=True
        )
        summarize_task = Task(
            agent=summarizer,
            description=f"Summarize these notes:\n{note}",
            expected_output="A concise summary of the key concepts"
        )
        crew = Crew(agents=[summarizer], tasks=[summarize_task], verbose=True)
        summary = crew.kickoff()
        st.success(summary)

elif page == "Flashcards":
    st.title("🧠 Flashcard Generator")
    topic = st.text_area("Enter a topic or summary:")
    if st.button("Generate Flashcards"):
        flashcard_maker = Agent(
            role="Flashcard Generator",
            goal="Create flashcards from summaries",
            backstory="A memory coach specializing in spaced repetition",
            #tools=[gemini_tool],
            llm = gemini_llm,
            verbose=True
        )
        flashcard_task = Task(
            agent=flashcard_maker,
            description=f"Generate 3 flashcards from this topic:\n{topic}",
            expected_output="Flashcards in Q&A format"
        )
        crew = Crew(agents=[flashcard_maker], tasks=[flashcard_task], verbose=True)
        output = crew.kickoff()
        for line in output.split('\n'):
            if line.startswith("Q:"):
                st.markdown(f"<div class='flashcard'><strong>{line}</strong>", unsafe_allow_html=True)
            elif line.startswith("A:"):
                st.markdown(f"{line}</div>", unsafe_allow_html=True)

elif page == "Quiz Master":
    st.title("❓ Quiz Master")
    quiz_topic = st.text_area("Enter a topic for quiz:")
    if st.button("Generate Quiz"):
        quiz_master = Agent(
            role="Quiz Master",
            goal="Create a short quiz from study notes",
            backstory="An expert in educational assessment",
            #tools=[gemini_tool],
            llm = gemini_llm,
            verbose=True
        )
        quiz_task = Task(
            agent=quiz_master,
            description=f"Generate 3 multiple-choice questions from this topic:\n{quiz_topic}",
            expected_output="Questions with 4 options and correct answers"
        )
        crew = Crew(agents=[quiz_master], tasks=[quiz_task], verbose=True)
        output = crew.kickoff()
        blocks = output.split("\n\n")
        for block in blocks:
            st.markdown(f"<div class='quiz'>{block}</div>", unsafe_allow_html=True)

elif page == "Tutor Chat":
    st.title("👨‍🏫 Tutor Agent")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask your tutor a question:")
    if st.button("Send"):
        tutor = Agent(
            role="Tutor",
            goal="Answer student questions based on study notes",
            backstory="A friendly and knowledgeable medical academic tutor",
            #tools=[gemini_tool],
            llm = gemini_llm,
            verbose=True
        )
        tutor_task = Task(
            agent=tutor,
            description=f"Answer this question:\n{user_input}",
            expected_output="A clear and helpful explanation"
        )
        crew = Crew(agents=[tutor], tasks=[tutor_task], verbose=True)
        response = crew.kickoff()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    for msg in st.session_state.chat_history:
        st.markdown(f"""
            <div class="chat-bubble">
            <strong>{msg['role'].capitalize()}:</strong> {msg['content']}
            </div>
        """, unsafe_allow_html=True)
