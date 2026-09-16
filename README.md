# 🎓 AI Study Buddy

AI Study Buddy is a Generative AI-powered learning application built with Python and Streamlit.

It helps students learn and revise topics by generating explanations, summaries, interactive quizzes, and flashcards using a Large Language Model through the Groq API.

---

## ✨ Features

### 💡 Explain Topics
Enter any topic and receive an AI-generated explanation based on your selected difficulty level.

### 📝 Summarize Notes
Paste study notes or text and generate a concise, structured summary.

### ❓ Interactive Quiz
Generate a 5-question multiple-choice quiz using AI.

The application allows users to:
- Select answers
- Submit the quiz
- Receive a score
- View correct answers
- Read AI-generated explanations

### 🧠 Flashcards
Generate revision flashcards automatically for any topic.

### 🎯 Difficulty Levels
Choose between:
- Beginner
- Intermediate
- Advanced

### 📏 Response Length
Choose:
- Short
- Medium
- Detailed

### 📚 Study History
Recent study sessions are stored during the active Streamlit session.

### ⬇️ Download Responses
AI-generated study notes can be downloaded as a text file.

### 🌙 Light and Dark Mode
The application supports customized light and dark themes.

---

# 🖥️ Application Interface

The application contains three main tabs:

### 🏠 Dashboard
Used to configure the AI, enter a topic, and generate study material.

### 🧩 Quiz
Used to complete AI-generated quizzes and view results.

### 📚 History
Displays recent study sessions.

---

# 🧠 How Generative AI Works in This Project

The basic workflow is:

```text
User Input
    ↓
Prompt Engineering
    ↓
Groq API
    ↓
Large Language Model
    ↓
AI Generated Response
    ↓
Streamlit Dashboard
```

The user enters a topic or notes.

The application creates a structured prompt based on:

- Selected AI mode
- Difficulty level
- Response length
- User input

The prompt is sent to the Large Language Model through the Groq API.

The model then generates the requested learning material.

For quizzes, the AI returns structured JSON data containing:

```json
{
  "questions": [
    {
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0,
      "explanation": "Explanation"
    }
  ]
}
```

The Python application processes this JSON and converts it into an interactive quiz.

---

# 🛠️ Technologies Used

- Python
- Streamlit
- Groq API
- Generative AI
- Large Language Models
- Prompt Engineering
- JSON
- Python Dotenv
- HTML/CSS styling

---

# 🤖 AI Model

The application currently uses:

```text
openai/gpt-oss-120b
```

through the Groq API.

---

# 📁 Project Structure

```text
GenAI-Study-Buddy/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

The `.env` file contains the private Groq API key and must not be uploaded to GitHub.

---

# 🔐 Environment Variables

Create a `.env` file inside the project directory.

Add:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Never upload your `.env` file or API key to GitHub.

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/GenAI-Study-Buddy.git
```

Move into the project directory:

```bash
cd GenAI-Study-Buddy
```

---

## 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Add your Groq API key

Create:

```text
.env
```

and add:

```text
GROQ_API_KEY=your_groq_api_key_here
```

---

# ▶️ Run the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Streamlit will normally open:

```text
http://localhost:8501
```

in your browser.

---

# 📦 Requirements

The project uses:

```text
streamlit
groq
python-dotenv
```

---

# 🔒 Security

The `.gitignore` file prevents sensitive and unnecessary files from being uploaded.

Example:

```text
venv/
.env
__pycache__/
*.pyc
.DS_Store
```

Never commit API keys to a public repository.

---

# 🎓 Generative AI Concepts Demonstrated

This project demonstrates:

- Large Language Model integration
- Prompt engineering
- System prompts
- Dynamic prompt generation
- AI text generation
- Structured AI output
- JSON parsing
- Generative quizzes
- AI-generated flashcards
- Session state
- API integration
- Interactive AI applications

---

# 🚀 Future Improvements

Possible future additions include:

- User authentication
- Persistent database storage
- PDF upload
- Chat with documents
- RAG
- Voice input
- Personalized study plans
- Quiz analytics
- Saved flashcards
- Cloud deployment

---

# 👨‍💻 Project Purpose

AI Study Buddy was developed as a practical project for understanding how Generative AI applications work.

The project demonstrates how a frontend interface can communicate with a Large Language Model using an API and transform generated AI output into an interactive application.

---

## ⭐ AI Study Buddy

Learn smarter. Revise faster. Test yourself with Generative AI.