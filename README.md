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
So we are Hallucin-AI-tors! We are a team of enthusiasts who decided to try something new this time that none of us have ever done before!

*Behave Yourself* is an Agentic AI platform designed to assist your daily developer needs. It removes the tedious, often time taking task of creating and maintaining Behavior-Driven Development (BDD) test suites and automates the entire process. It integrates with GitHub and JIRA to streamline the process of managing repositories and tasks.


## 🎥 Demo
📹 [Video Demo](https://drive.google.com/file/d/1LNvaQby6qRmAEImGjKTyE2e8BexkL16U/view)  
🖼️ Powerpoint Presentation: (https://docs.google.com/presentation/d/16klVNXX4uKVC8XxEt5mELdikz8nVor4N3uA5cI1be7c/edit)

## 💡 Inspiration
The entire inspiration comes from some of us team members having to work on BDD Testing for our projects. And it is a complicated thing having to figure out the interconnection between the microservices and create the actual tests. Since we have been through this, we are demo-ing the solution using one of the exact systems that we have worked with before

## ⚙️ What It Does
So our system is basically an agent you can speak with. We have tried to make BDD testing for complex ecosystems completely No-Code! Through the conversation it tries to achieve the following for you:

- Analyses end to end how an application functions utilizing *Codebase*, *Jira*, *PRs* and *Database*
- Remembers configurations that you want it to utilize while creating Test Suites. It uses its Long Term Memory
- Automates the creation of BDD repositories using Test Suite templates
- Performs all code changes required
- Connects with JIRA for task tracking and management.
- Provides tools for analyzing repository structures and pull requests.
- It can provide you with *architecture diagrams* for the ecosystems as well, though currently only in ASCII. We didn't get time to implement image generation

## 🛠️ How We Built It
- **Our Backend**: Is build using Socket.io on top of a Python Flask server for real-time communication. It also hosts our agent
- **Agentic AI**: It is built on top of the entire Langchain toolset. We utilize langflow, langgraph and our own Custom Toolkits for the entire feature-set of the agent
- **Memory Architecture**: Our Agent has Long term memory capabilities that function using a RAG system. This allows configuration and recall over multiple conversations
- **GitHub Integration**: Using `PyGithub` for repository and PR management.
- **JIRA Integration**: Custom toolkit for task management using JIRA API

## 🚧 Challenges We Faced
- Agentic Framework since none of us have worked on it before
- Prompt engineering as it was hard to make the agent stop hallucinating data
- Coming up with a system for persistence and memory so it can tackle situations where it needs to update current test scenarios based on apst analysis
0- Handling edge cases in GitHub API interactions (e.g., missing forks or file conflicts).
- Ensuring compatibility with multiple repositories and frameworks.
- Managing real-time updates with Socket.IO. We think we made a nice UI

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
- 🔹 **Database**: MongoDB
- 🔹 **APIs**: GitHub API, JIRA API
- 🔹 **AI**: LangChain, Gemini

## 👥 Team
- **Additya Singhal** - [GitHub](https://github.com/UnknownAbyss) | [LinkedIn](https://www.linkedin.com/in/addityasinghal/)
- **Amisha Sinha** - [GitHub](https://github.com/Amisha-Sinha) | [LinkedIn](https://www.linkedin.com/in/amisha-sinha-202730240/)
- **Anubhav Srivastava** - [GitHub](https://github.com/Anubhav0611) | [LinkedIn](https://www.linkedin.com/in/ashrivastava1110/)
- **Anusha Panchumarthi** - [GitHub](https://github.com/Anusha-Panchumarthi) | [LinkedIn](https://www.linkedin.com/in/anusha-panchumarthi-bb161a229/)
- **Gaurang Rastogi** - [GitHub](https://github.com/GaurangRastogi) | [LinkedIn](https://www.linkedin.com/in/gaurangrastogi209/)
