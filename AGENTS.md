### `agent.md`

#### 1. Project Overview

**Project Name:** Internal Genius - A Knowledge Base Chatbot

This project is a full-stack web application that demonstrates a Retrieval-Augmented Generation (RAG) pipeline. Its purpose is to allow users to upload internal documents and ask questions about their content in natural language. The system retrieves relevant information from the documents and generates a grounded response, complete with citations.

The project is fully containerized using Docker and is structured with a distinct backend and a frontend.

* `backend/`: Contains all Python code for the RAG pipeline, API, and document processing, following a **Clean Code Architecture**.
* `frontend/`: Contains the React application.
* `docker/`: Contains `Dockerfile` and `docker-compose.yml` for containerizing the application.
* `data/`: A placeholder for documents used during local development and testing.

#### 2. Development Workflow

The development process is iterative, structured, and containerized. The coding agent should operate in a task-oriented manner, focusing on small, verifiable changes.

* **Task Breakdown:** All tasks should be broken down into small, single-purpose units. A pull request (PR) should address a single, well-defined problem.
* **Test-Driven Development (TDD):** For new features or bug fixes, tests should be written before or concurrently with the code implementation. The agent must ensure that all relevant tests pass before marking a task as complete.
* **Containerization:** All local development and testing must be performed within the Docker environment using `docker compose`.
* **Refactoring:** Refactoring should be done as a separate, focused task. Avoid mixing refactoring changes with new feature implementation in a single PR.
* **Documentation:** All new functions, classes, and complex logic must be accompanied by clear docstrings and comments. Update existing documentation (`README.md`, `agent.md`, etc.) as needed.

#### 3. Core Technologies and Architecture

The agent must adhere to the following technological and architectural conventions.

**Backend (`backend/`):**
* **Language:** Python 3.14
* **Web Framework:** **FastAPI**.
* **RAG Pipeline:**
    * **Orchestration:** **LangGraph** is the core framework for building the RAG pipeline. It should be used to define the state, nodes, and edges of the workflow.
    * **Document Processing:** **Docling** is the primary library for ingesting and parsing various document types.
    * **Embedding Model:** **`gemini-embedding-001`** via the Google AI SDK.
    * **LLM:** **Gemini 2.5 Flash** via the Google AI SDK.
    * **Vector Database:** **ChromaDB**.
* **Clean Architecture:**
    * The backend code must be organized into distinct layers to separate concerns and promote testability and maintainability.
    * `backend/api/`: The API layer. Contains FastAPI routers, endpoints, and data schemas (Pydantic models) for the API.
    * `backend/services/`: The business logic layer. Contains the core logic of the RAG pipeline, including document processing and query handling. This layer should be independent of the framework.
    * `backend/repositories/`: The data access layer. Contains the logic for interacting with the vector database (ChromaDB).
    * `backend/models/`: Contains the data models used across different layers.

**Frontend (`frontend/`):**
* **Framework:** **React**. Use functional components with hooks. Avoid class-based components.
* **Styling:** Use standard CSS or a library like Tailwind CSS. Do not use inline styles.
* **API Calls:** All communication with the backend should be done using a library like `axios` or the native `fetch` API.

**Containerization (`docker/`):**
* **Docker:** The project will be run using **Docker**.
* **Docker Compose:** **`docker-compose.yml`** will be used to define and run the multi-container application (backend and frontend).
* **Dockerfiles:** Separate `Dockerfile`s should be created for the backend and frontend. These should be optimized for production by using multi-stage builds to keep final image sizes small.

#### 4. Coding Conventions and Style

The agent must follow these conventions to ensure code consistency and maintainability.

* **Python:** All Python code must strictly adhere to the PEP 8 style guide.
* **Type Hinting:** Use type hints for all function parameters and return values. This is crucial for maintainability and clarity.
* **Naming Conventions:**
    * **Python:** Use `snake_case` for function and variable names. Use `PascalCase` for class names.
    * **React:** Use `PascalCase` for component names and `camelCase` for variables and functions.
* **Code Formatting & Linting:** Use **`ruff`** for both formatting and linting. The agent should understand that formatting is automatically applied on save.

#### 5. Build and Test Commands

The agent must use the following commands to set up the environment, run the application, and execute tests.

* **Full Project (via Docker Compose):**
    * `docker compose up --build`: Build and run the entire application.
    * `docker compose down`: Stop and remove the containers.
* **Testing:**
    * `docker compose run --rm backend pytest`: Run the backend test suite.
    * `docker compose run --rm frontend pnpm test`: Run the frontend test suite.

The agent must pass all tests before a commit.

---

#### Commit Guidelines

- Follow Conventional Commits specification (e.g., `feat: Add new user registration`, `fix: Correct login bug`).
- Commit messages should be clear, concise, and explain the "what" and "why" of the changes.

#### 6. Dos and Don'ts

**DO:**
* **Do** ask for clarification if a task is unclear.
* **Do** write clear, concise, and well-commented code.
* **Do** adhere to the defined clean architecture. Separate concerns by placing code in the correct layers (`api`, `services`, `repositories`).
* **Do** use environment variables for all secrets (API keys, etc.) and expose them via Docker.
* **Do** use `docker compose` for all local development commands.
* **Do** create dedicated, small commits for each logical change.
* **Do** use the specified technologies and follow the architectural guidelines.
* **Do** use LangChain's evaluation tools to verify the quality of the pipeline's output.

**DON'T:**
* **Don't** mix business logic with API routing logic. Keep them in their respective layers.
* **Don't** install dependencies directly on the host machine. Use `uv` inside the container's build process.
* **Don't** make large, monolithic commits that mix multiple changes.
* **Don't** generate code that does not pass the established tests or linting checks.
* **Don't** hardcode API keys or sensitive information. Use Docker environment variables.