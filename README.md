# 🚀 Keyword Intelligence Agent

### 🔍 AI-Powered SEO Intelligence Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-purple)
![Stars](https://img.shields.io/github/stars/yourusername/Keyword-Intelligence-Agent?style=social)

---

## ✨ What is this?

**Keyword Intelligence Agent** is a powerful AI-driven SEO system that:

* Simulates real Google search behavior
* Extracts high-ranking SEO keywords
* Generates optimized blog titles
* Builds intelligent blog outlines

👉 All in a **3-step structured workflow** designed for real-world SEO content creation.

---

## ⚡ Core Features

### 🔎 1. Smart Keyword & URL Discovery

* Fetches **top-ranking Google pages**
* Extracts **high-performing SEO keywords**
* Filters broken / low-quality URLs

---

### 💡 2. SEO Title Generation

* Generates **5 optimized titles**
* Matches **search intent**
* Forces:

  * Keyword inclusion
  * Number-based titles
  * Strong SEO patterns

---

### 📑 3. Intelligent Outline Generation

* Detects content type automatically:

  * Guide / Listicle / Comparison / How-To
* Generates:

  * **3–8 H2 sections**
  * **2–4 H3 per section**
* Avoids:

  * Repetition
  * Weak headings
  * Poor grammar

---

### 🎯 Advanced Capabilities

* ✅ Real-time streaming UI
* ✅ Step-by-step interactive workflow
* ✅ Keyword selection (chips)
* ✅ Title selection (cards)
* ✅ Clean URL validation pipeline
* ✅ Retry logic for failed generations
* ✅ Fully modular architecture

---

## 🧠 How It Works

### 🔄 3-Step AI Pipeline

```
[ Step 1 ]
Get Keywords & URLs
        ↓
[ Step 2 ]
Generate Titles (based on selected keyword)
        ↓
[ Step 3 ]
Generate Outline (based on selected title + keyword)
```

---

### 🧩 Flow Explanation

1️⃣ **Keywords & URLs**

* AI simulates Google search
* Extracts top 10 pages
* Returns 15 SEO keywords

2️⃣ **Title Generation**

* User selects keyword
* AI generates optimized titles

3️⃣ **Outline Generation**

* User selects title
* AI builds structured blog outline

---

## 🛠 Tech Stack

| Layer          | Technology       |
| -------------- | ---------------- |
| Backend        | FastAPI          |
| UI             | FastHTML         |
| AI Engine      | Gemini 2.5 Flash |
| Server         | Uvicorn          |
| Language       | Python           |
| Env Management | python-dotenv    |
| Networking     | Requests         |

---

## 📁 Project Structure

```bash
Keyword_Chatbot_Simple/
├── agent/
│   └── keyword_agent.py
├── llm_clients/
│   └── gemini_client.py
├── utils/
│   └── url_cleaner.py
├── api.py
├── ui_app.py
├── main.py
├── config.py
├── .env
└── requirements.txt
```

---

## 🚀 Getting Started

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/Keyword-Intelligence-Agent.git
cd Keyword-Intelligence-Agent
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate   # Windows
# or
source venv/bin/activate   # Mac/Linux
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment

Create `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

### 5️⃣ Run the App

```bash
uvicorn ui_app:app --reload
```

---

### 🌐 Open in Browser

```
http://127.0.0.1:8000
```

---

## 📡 API Reference

| Method | Endpoint       | Description     |
| ------ | -------------- | --------------- |
| GET    | /              | UI              |
| GET    | /stream/step1  | Keywords + URLs |
| GET    | /stream/step2  | Titles          |
| GET    | /stream/step3  | Outline         |
| GET    | /stream        | Full pipeline   |
| POST   | /analyze-topic | REST API        |

---

## 📊 Sample Output

<details>
<summary>Click to expand</summary>

### 🧠 Topic

Machine Learning

### 🔗 URLs

* IBM
* Google Cloud
* Coursera
* Wikipedia
* AWS

### 🔥 Keywords

machine learning, AI, deep learning, neural networks...

### 💡 Titles

* What is Machine Learning? A Complete Guide
* 7 Types of Machine Learning Explained

### 📑 Outline

* H2: What is Machine Learning
* H2: How It Works
* H2: Types of ML
* H2: Applications
* H2: Future Trends

</details>

---

## ⚙️ Configuration

Environment variables:

```env
GEMINI_API_KEY=your_key_here
```

---

## 🔐 Security Notes

* ❌ Never upload `.env`
* ❌ Never expose API keys
* ✅ Use `.gitignore`

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

---

## 📜 License

MIT License © 2026

---

## 🌟 Support

If you like this project:

⭐ Star the repository
📢 Share with others
🚀 Build on top of it

---

## 💬 Final Thought

> AI + SEO + Automation = Future of Content Intelligence

---

🔥 **Build smarter. Rank faster. Scale content with AI.**
