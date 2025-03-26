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
*Behave Yourself* is an AI-driven platform designed to assist developers in creating and maintaining Behavior-Driven Development (BDD) test suites. It integrates with GitHub and JIRA to streamline the process of managing repositories and tasks.

## 🎥 Demo
📹 [Video Demo](https://drive.google.com/file/d/1LNvaQby6qRmAEImGjKTyE2e8BexkL16U/view)  
🖼️ Screenshots: (https://docs.google.com/presentation/d/16klVNXX4uKVC8XxEt5mELdikz8nVor4N3uA5cI1be7c/edit)

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
   git clone https://github.com/ewfx/catfe-hallucin-aitors
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
5. To run ui go to /ui
   ```sh
   npm i --force
   npm run dev
   ```

## 🏗️ Tech Stack
- 🔹 **Backend**: Flask, Python
- 🔹 **BDD Framework**: Karate
- 🔹 **Database**: MongoDB
- 🔹 **APIs**: GitHub API, JIRA API
- 🔹 **Other Tools**: LangChain, OpenAI API

## 👥 Team
- **Additya Singhal** - [GitHub](https://github.com/UnknownAbyss) | [LinkedIn](https://www.linkedin.com/in/addityasinghal/)
- **Amisha Sinha** - [GitHub](https://github.com/Amisha-Sinha) | [LinkedIn](https://www.linkedin.com/in/amisha-sinha-202730240/)
- **Anubhav Srivastava** - [GitHub](https://github.com/Anubhav0611) | [LinkedIn](https://www.linkedin.com/in/ashrivastava1110/)
- **Anusha Panchumarthi** - [GitHub](https://github.com/Anusha-Panchumarthi) | [LinkedIn](https://www.linkedin.com/in/anusha-panchumarthi-bb161a229/)
- **Gaurang Rastogi** - [GitHub](https://github.com/GaurangRastogi) | [LinkedIn](https://www.linkedin.com/in/gaurangrastogi209/)
