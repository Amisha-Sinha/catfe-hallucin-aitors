# 🚀 Behave Yourself

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
Behave Yourself is an AI-driven platform designed to assist developers in creating and maintaining Behavior-Driven Development (BDD) test suites. It integrates with GitHub and JIRA to streamline the process of managing repositories and tasks.

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
The project was inspired by the need to simplify the creation and upkeep of BDD test repositories, ensuring seamless integration with existing workflows.

## ⚙️ What It Does
- Automates the creation of BDD repositories using a Karate framework template.
- Integrates with GitHub for repository management (forking, pushing commits, raising PRs).
- Connects with JIRA for task tracking and management.
- Provides tools for analyzing repository structures and pull requests.

## 🛠️ How We Built It
- **Backend**: Python with Flask for API and Socket.IO for real-time communication.
- **GitHub Integration**: Using `PyGithub` for repository and PR management.
- **JIRA Integration**: Custom toolkit for task management.
- **BDD Framework**: Karate template for test suite creation.
- **Environment Management**: `.env` files for secure configuration.

## 🚧 Challenges We Faced
- Handling edge cases in GitHub API interactions (e.g., missing forks or file conflicts).
- Ensuring compatibility with multiple repositories and frameworks.
- Managing real-time updates with Socket.IO.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/your-repo.git
   ```
2. Set up environment variables in a `.env` file:
   ```env
   GITHUB_AUTH_TOKEN=your_github_token
   JIRA_EMAIL=your_jira_email
   JIRA_API_TOKEN=your_jira_api_token
   PAYMENTS_URI=your_payments_db_uri
   MEMORIES_URI=your_memories_db_uri
   ```
3. Install dependencies  
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask app  
   ```sh
   python src/main.py
   ```

## 🏗️ Tech Stack
- 🔹 **Backend**: Flask, Python
- 🔹 **BDD Framework**: Karate
- 🔹 **Database**: MongoDB
- 🔹 **APIs**: GitHub API, JIRA API
- 🔹 **Other Tools**: LangChain, OpenAI API

## 👥 Team
- **Additya Singhal** - [GitHub](#) | [LinkedIn](#)
- **Amisha Sinha** - [GitHub](#) | [LinkedIn](#)
- **Anubhav Srivastava** - [GitHub](#) | [LinkedIn](#)
- **Anusha Panchumarthi** - [GitHub](#) | [LinkedIn](#)
- **Gaurang Rastogi** - [GitHub](#) | [LinkedIn](#)
