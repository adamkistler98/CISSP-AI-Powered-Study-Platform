# CISSP Exam Architect | AI-Powered Study Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B)
![API](https://img.shields.io/badge/Backend-Google%20Gemini%201.5-4285F4)
![Status](https://img.shields.io/badge/Status-Production-success)

## 📋 Project Overview
**CISSP Exam Architect** is a resilient, cloud-native web application designed to assist cybersecurity professionals in preparing for the **Certified Information Systems Security Professional (CISSP)** exam.

Unlike static question banks, this tool leverages **Generative AI (Google Gemini 1.5 Flash)** to create unique, scenario-based questions on demand. It features a professional "Exam Mode" interface simulating real-world testing environments (Pearson VUE style).

### 🛡️ Key Engineering Features
* **Fault-Tolerant Architecture:** Implements a **"Circuit Breaker" pattern**. If the external AI API experiences downtime or rate-limiting (HTTP 429/500), the system automatically degrades gracefully to a local, pre-encrypted database of high-value questions.
* **Zero-Dependency Connectivity:** Bypasses heavy SDKs in favor of lightweight, "bare metal" REST API calls (`requests`), reducing container size and eliminating dependency conflicts.
* **Dynamic Prompt Engineering:** Context-aware prompts generate questions across 3 difficulty levels (Associate, Professional, Expert) and 3 formats (Multiple Choice, True/False, Executive Brief).

## 🚀 Application Demo

### Core Functionality
1.  **Domain Selection:** Choose from all 8 CISSP domains (e.g., Security & Risk Management, IAM, Asset Security).
2.  **Difficulty Scaling:** Adjust complexity from standard definitions to complex "Scenario-based" analysis.
3.  **Instant Feedback:** AI provides detailed explanations citing NIST/ISO standards for every answer.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python-based reactive UI)
* **Backend Intelligence:** Google Gemini 1.5 Flash (via REST API)
* **Deployment:** Streamlit Cloud / Docker Container compatible
* **Version Control:** GitLab CI/CD

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.8+
* Google AI Studio API Key

### 1. Clone the Repository
```bash
git clone [https://gitlab.com/your-username/cissp-architect.git](https://gitlab.com/your-username/cissp-architect.git)
cd cissp-architect

├── app.py                # Main application logic & Circuit Breaker
├── requirements.txt      # Lightweight dependencies (Streamlit, Requests)
├── .gitignore            # Security exclusions
└── README.md             # Documentation

Ini, TOML
GEMINI_API_KEY=your_actual_api_key_here
