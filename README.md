# 🎓 AI Study Buddy

AI Study Buddy is a Generative AI-powered learning application built with Python and Streamlit.

It helps students learn and revise topics by generating explanations, summaries, interactive quizzes, and flashcards using a Large Language Model through the Groq API.

---

## ✨ Features

### 🧠 8 Study Modes
- **💡 Explain Topic** – step-by-step explanations with examples and common mistakes
- **📝 Summarize Notes** – structured summaries with a key-terms table
- **❓ Generate Quiz** – 3 to 40 interactive multiple-choice questions
- **🃏 Flashcards** – flip cards with hints, "I knew it" tracking and shuffle
- **🗺️ Mind Map** – a visual, colour-coded map of the whole topic
- **📅 Study Plan** – a day-by-day plan based on your available days and minutes per day
- **🎭 Explain with Analogy** – learn through creative real-life comparisons
- **🧑‍🏫 Feynman Check** – explain a topic in your own words and get scored (0–100) on strengths, gaps and misconceptions

### 💬 AI Tutor Chat
A streaming, multi-turn chat with four tutor personalities: Friendly Tutor, Socratic Coach, Strict Examiner and Explain Like I'm 5.

### 📎 Study From Your Own Material & Photos
Upload one or more PDF, TXT or MD files, or photos of your notebook or textbook (JPG, PNG, WEBP). Photos are read by a vision model (`qwen/qwen3.8-27b` on Groq), and every mode and the chat then use that material as the source.

### 🧠 Mistake Coach
After a quiz, the AI explains every wrong answer, gives memory tricks and suggests practice questions.

### 🏅 Streaks, Badges & Progress
Daily study streaks, 7 unlockable badges, study-session counts and a quiz-score trend chart. Progress is saved privately in each student's own browser, so friends never see each other's stats.

### ✨ Smart Navigation
After generating a quiz or flashcards, the app jumps straight to that tab. Other results scroll into view automatically.

### 💬 Rotating Motivational Quotes
A fresh, random set of motivational quotes animates through the header every time the app is opened.

### 🌍 Multi-language Answers
Get answers in English, Urdu, Arabic, Hindi, French or Spanish.

### ⬇️ Downloads
Download notes, mind map outlines, flashcard decks and your full study history as plain `.txt` files that open on any device.

### 🌙 Light and Dark Mode
The application supports customized light and dark themes.

---

# 🖥️ Application Interface

- **🏠 Dashboard** – choose a mode, upload material and generate study content
- **💬 AI Tutor Chat** – chat with your AI tutor
- **🧩 Quiz** – answer quizzes, see results and get mistake coaching
- **🃏 Flashcards** – revise with flip cards
- **📈 Progress** – streaks, badges, sessions and quiz trends
- **📚 History** – search and export this session's study history

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
- pypdf
- Graphviz (mind maps)
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

# 🔗 Sharing the App

Deploy the app (for example on Streamlit Community Cloud) and share its link. It works in any phone or laptop browser.

To keep it one tap away, students can save the link to their home screen:
- **Android (Chrome):** ⋮ menu → **Add to Home screen**
- **iPhone (Safari):** **Share** → **Add to Home Screen**

The `static/` folder holds the app icon and name used for that shortcut.

---

# 📦 Requirements

The project uses:

```text
streamlit
groq
python-dotenv
pypdf
pillow
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