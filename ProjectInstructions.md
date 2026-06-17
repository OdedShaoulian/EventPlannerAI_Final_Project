# Artificial Intelligence-Based App Development – Final Project

## Overview

Design and develop an original AI-based application of your choice. The app must solve a real problem and demonstrate the technologies learned during the course. You can choose any field, such as education, business, healthcare, gaming, tourism, productivity, sports, entertainment, or any other area that interests you.

The evaluation will consider the originality of the idea, the value it provides, and the quality of the solution.

## Technical Requirements

The application must include all of the following components:

### 1. Conversational AI

The app must allow users to communicate with an AI assistant using natural language.
**Must use:**

* OpenAI Responses API

**Examples of capabilities:**

* Answering questions
* Providing recommendations
* Content generation
* Providing explanations

### 2. Multi-Modal Capability

The app must allow the user to upload at least one of the following input types:

* Image
* Audio file

**The AI must:**

* Analyze the uploaded input
* Use the extracted information as part of the response

**Must use one of the following OpenAI capabilities:**

* Vision Input (Image)
* Audio Input / Speech-to-Text (Audio)

**Examples of Image capabilities:**

* Image understanding
* Object detection
* Screenshot analysis
* Diagram explanation
* OCR and text extraction

**Examples of Audio capabilities:**

* Speech-to-text transcription
* Conversation content analysis
* Recording summarization
* Extracting insights from an interview or meeting

### 3. RAG – Retrieval-Augmented Generation

The app must include a custom knowledge base. Users should be able to ask questions where the answers are based on information retrieved from the knowledge base.
**Must use:**

* OpenAI Embeddings API
* ChromaDB

**Examples of knowledge bases:**

* Company documents
* Product manuals
* Study materials
* Academic papers
* Any other database relevant to your app

### 4. Additional OpenAI Capability

The app must include at least one additional OpenAI capability beyond the requirements listed above.
**Examples:**

* Text-to-Speech (TTS)
* Image Generation
* Function Calling
* Structured Outputs
* JSON Responses

### 5. OpenAI Requirements Summary

The project must use at least three OpenAI capabilities or APIs:
**Mandatory:**

1. Responses API
2. Embeddings API
3. At least one of the following: Vision Input **OR** Audio Input / Speech-to-Text

**In addition:**
4.  At least one additional OpenAI capability of your choice.

### 6. User Interface

The app must include a user interface of your choice.
**Possible options:**

* Web app
* Desktop app
* Command Line Interface (CLI) app

The interface must clearly demonstrate all the capabilities required in the project.

### 7. Submission via GitHub

You must submit a link to a GitHub repository containing the project.
**The repository must include:**

* Full source code
* `README.md`
* `requirements.txt`

### 8. README.md Requirements

The README file must include the following sections:

* **Project Name:** The name of the app.
* **Project Description:** A brief explanation including: What problem the app solves, who the target audience is, and how AI is used in the solution.
* **Core Capabilities:** Describe all the main capabilities of the app. This section must include: Conversational AI capability, Multi-modal capability (image or audio), RAG capability, and the additional OpenAI capability you used.
* **OpenAI APIs Used:** Detail all the OpenAI APIs and capabilities used in the project.
* **Installation Instructions:** Explain how to install and run the project. Example:
* `pip install -r requirements.txt`
* `python app.py`


* **Environment Variables:** Explain which environment variables are required. Example: `OPENAI_API_KEY=your_api_key_here`. ❗ **Do not upload API keys to GitHub.**
* **Demo Instructions:** Provide clear instructions for testing the app. Must include: An example of a user question or request, an example of uploading an image or audio file, and an example of a RAG-based question.
* **Team Members:** List all team members.

### requirements.txt

The repository must include a file named `requirements.txt`. This file contains all the Python libraries required to run the project.
**Example:**

* `openai`
* `chromadb`
* `python-dotenv`
* `pypdf`

Anyone downloading the project should be able to install all dependencies using: `pip install -r requirements.txt`

### 9. Creativity

You are encouraged to be creative and build a unique solution. Choose a problem that interests you and demonstrate how Generative AI can be used to create a solution with real value for users. There are no restrictions on the project's domain, as long as all technical requirements are met.

### 10. Submission

You must submit:

* **GitHub Repository Link:** The repository must contain the full source code, `README.md`, `requirements.txt`, and any additional files required to run the system (such as a database of files for RAG).
* **Project Presentation:** Presentation duration: 5–10 minutes. The presentation should include: The chosen problem, the proposed solution, the general architecture, OpenAI technologies used, and a short demo of the system.
* **Live Demo (Video):** You must record a real-time video of the system demonstrating: A conversation with the AI, the multi-modal capability (image or audio), a RAG query, and the chosen additional capability.

### 11. Project Defense

In addition to submitting the project, there will be a project defense in a Zoom meeting (date to be scheduled separately). During the defense, each team will present their project, explain the implementation, and perform a live demo of the app.
**During the defense, you will be required to:**

* Present the problem the project solves.
* Explain the solution you developed.
* Present the general architecture of the system.
* Explain how OpenAI capabilities were integrated into the project.
* Explain how you implemented the RAG component.
* Explain how you implemented the multi-modal capability (image or audio).
* Explain the additional capability you chose.
* Demonstrate the app in action.
* Answer questions regarding the code, design, technological decisions, and how the system works.

**Live Demo:**
During the defense, you must demonstrate:

* A conversation with the AI assistant.
* Uploading an image or audio file and analyzing it.
* A question based on the RAG knowledge base.
* The additional capability chosen in the project.

It is important to come prepared to explain not only *what* the app does, but also *how* it works.

---

**Good Luck!**
Good luck, and have fun building your AI app!