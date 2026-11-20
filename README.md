<p align="center">
  <img src="docs/logos/logo.png" alt="AgentOps-OS Logo" width="150">
</p>

<h1 align="center">AgentOps-OS</h1>

<p align="center">
  <strong>A Unified Operations Platform for AI Agents</strong>
</p>

<p align="center">
  Build. Orchestrate. Evaluate. Observe.
</p>

<p align="center">
  Design, execute, manage, and monitor AI agents and intelligent workflows through one unified full-stack platform.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/pgvector-Vector%20Search-336791?style=for-the-badge" alt="pgvector">
  <img src="https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
  <img src="https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project%20Status-Active%20Development-orange?style=for-the-badge" alt="Project Status">
</p>

<p align="center">
  <a href="https://github.com/vivekgadhe/AgentOps-OS">
    <strong>GitHub Repository</strong>
  </a>
  &nbsp; • &nbsp;
  <a href="https://github.com/vivekgadhe/AgentOps-OS/issues">
    <strong>Report an Issue</strong>
  </a>
</p>

---

## 🖥️ Application Preview

<p align="center">
  <img
    src="docs/screenshots/agentops-overview.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

<p align="center">
  <em>
    Explore the AgentOps-OS interface — from authentication and workflow orchestration
    to AI agent interactions, knowledge management, analytics, memory, and administration.
  </em>
</p>

---

## 🧭 Explore AgentOps-OS

<p align="center">
  <a href="#-key-features">✨ Features</a>
  &nbsp; • &nbsp;
  <a href="#-system-architecture">🏗️ Architecture</a>
  &nbsp; • &nbsp;
  <a href="#-technology-stack">🛠️ Technology Stack</a>
  &nbsp; • &nbsp;
  <a href="#-installation-guide">🚀 Installation</a>
</p>

<p align="center">
  <a href="#-api-documentation">📡 API Documentation</a>
  &nbsp; • &nbsp;
  <a href="#-testing-and-quality-assurance">🧪 Testing</a>
  &nbsp; • &nbsp;
  <a href="#-verification-and-evidence">✅ Verification</a>
  &nbsp; • &nbsp;
  <a href="#-developer">👨‍💻 Developer</a>
</p>

---

# 📖 Project Overview

**AgentOps-OS** is a full-stack AI Agent Operations platform designed to build, orchestrate, manage, and monitor intelligent AI agents and automated workflows through a unified application.

As AI agents become increasingly capable of performing complex, multi-step tasks, managing their execution, knowledge, memory, tools, approvals, and operational activity becomes an important engineering challenge.

AgentOps-OS brings these capabilities together in one platform, providing developers with a visual workspace to create workflows, execute agent tasks, connect knowledge sources, manage persistent memory, review human approvals, configure AI providers, and monitor system activity.

Built using **Python, FastAPI, React, TypeScript, PostgreSQL, and pgvector**, the platform combines modern backend engineering with practical AI application development. It also supports local LLM integration through **Ollama**, allowing developers to experiment with locally running models.

### 🎯 What Does AgentOps-OS Provide?

AgentOps-OS brings together several important capabilities of modern AI agent systems:

- **AI Agent Management:** Interact with specialized AI capabilities for analysis, planning, actions, and report generation.

- **Visual Workflow Orchestration:** Design and execute workflows using configurable steps, tools, agent tasks, and execution dependencies.

- **Workflow Execution Management:** Track workflow runs, monitor task progress, and inspect execution results.

- **Human-in-the-Loop Approvals:** Introduce human review and approval controls for actions requiring oversight.

- **Knowledge Management and RAG:** Upload documents, process knowledge sources, perform semantic retrieval, and provide relevant context to AI applications.

- **Persistent Agent Memory:** Store, retrieve, search, and manage memory associated with agent conversations and activities.

- **AI Provider Management:** Configure and manage supported AI providers, including local model integration through Ollama.

- **Analytics and Observability:** Record operational telemetry and monitor workflow, agent, provider, and system activity.

- **Authentication and Access Control:** Provide account registration, email OTP verification, authentication, and role-based access.

### 🏗️ Engineering Vision

The primary engineering objective behind AgentOps-OS is to explore how individual AI capabilities can be integrated into a cohesive, maintainable, and extensible software platform.

Rather than treating an AI agent as an isolated chatbot, the project focuses on the infrastructure surrounding agent execution:

- How agents are configured and invoked.
- How multi-step workflows are organized and executed.
- How tools and external services are integrated.
- How knowledge is retrieved and supplied as context.
- How memory is maintained across interactions.
- How human oversight is incorporated into execution.
- How provider activity and system operations are monitored.
- How the complete application is tested and maintained.

### 💡 Project Philosophy

**AI agents need more than intelligence. They need infrastructure, orchestration, memory, control, and observability.**

AgentOps-OS explores these engineering principles by bringing them together in one full-stack application.

## 🎯 Problem Statement

AI agents are evolving beyond simple question-and-answer applications. Modern AI-powered systems can interact with tools, retrieve information from knowledge sources, maintain context, execute multi-step tasks, and coordinate different capabilities to accomplish complex objectives.

However, building an individual AI agent is only one part of the engineering challenge. Developers must also build and manage the infrastructure required to execute, coordinate, control, and monitor these agents reliably.

As AI applications become more complex, several challenges emerge.

### 1. Fragmented Agent Development

Developers often build agents, tools, workflows, memory systems, and integrations as separate components.

Without a unified management layer, maintaining these components becomes difficult.

**Challenges:**
- Managing multiple specialized agents.
- Maintaining consistent configurations.
- Integrating different tools and services.
- Coordinating communication between components.
- Maintaining a clear view of the overall system.

### 2. Complex Workflow Orchestration

AI applications frequently require multiple steps to complete a task. These steps may involve agent execution, tool calls, conditional logic, and dependencies.

Managing these operations without a structured orchestration mechanism can make workflows difficult to understand and maintain.

**Challenges:**
- Defining multi-step execution workflows.
- Managing task dependencies and execution order.
- Tracking individual task states.
- Handling execution failures.
- Monitoring complete workflow runs.

### 3. Limited Execution Visibility

A successful final response does not necessarily explain everything that happened during an agent execution.

Developers need visibility into workflow runs, task activity, provider interactions, and execution outcomes.

**Challenges:**
- Understanding what happened during execution.
- Identifying failed or incomplete tasks.
- Tracking workflow and agent activity.
- Investigating execution errors.
- Measuring operational performance.

### 4. Lack of Human Oversight

Some AI-generated actions require human review before they can proceed.

Without an approval mechanism, it becomes difficult to introduce controlled checkpoints into automated workflows.

**Challenges:**
- Identifying actions that require approval.
- Pausing execution for human review.
- Recording approval decisions.
- Managing pending approval requests.
- Maintaining appropriate control over sensitive operations.

### 5. Knowledge Retrieval and Context Management

AI applications often need information from documents and other knowledge sources to produce relevant responses.

Connecting documents to an AI application is not enough. Developers must also manage document processing, indexing, retrieval, and the context supplied to the model.

**Challenges:**
- Processing and managing knowledge documents.
- Generating and storing embeddings.
- Performing semantic retrieval.
- Supplying relevant information to agents.
- Maintaining useful source context for responses.

### 6. Persistent Agent Memory

An AI interaction may require information from previous conversations or activities.

Without persistent memory management, applications can struggle to maintain useful context across separate interactions.

**Challenges:**
- Storing relevant information.
- Retrieving previously stored memories.
- Searching and managing memory records.
- Maintaining conversation history.
- Controlling memory updates and deletion.

### 7. AI Provider Dependency

AI applications may depend on different model providers, each with its own configuration, connectivity, and operational requirements.

Developers need flexibility to configure and manage provider integrations without tightly coupling application logic to a single provider.

**Challenges:**
- Integrating different AI providers.
- Managing provider configurations.
- Testing provider connectivity.
- Supporting locally running models.
- Managing provider-specific execution failures.

### 8. Insufficient Operational Observability

As AI systems grow, understanding their operational behavior becomes increasingly important.

Developers need structured information about application activity, agent executions, workflow performance, and provider interactions.

**Challenges:**
- Recording operational events.
- Tracking workflow and agent activity.
- Monitoring execution outcomes.
- Analyzing provider usage.
- Investigating operational issues.

### 9. Full-Stack Integration and Security

An AI agent platform must bring together frontend interfaces, backend services, databases, authentication, and AI integrations.

These components must work together while maintaining secure access and consistent application behavior.

**Challenges:**
- Designing reliable backend APIs.
- Managing authentication and authorization.
- Protecting application configuration and credentials.
- Maintaining database consistency.
- Testing frontend and backend integration.
- Keeping the application modular and maintainable.

---

### ⚠️ The Core Engineering Challenge

The central challenge is not simply creating an AI agent that can generate a response.

It is building the surrounding infrastructure that enables agents to be configured, orchestrated, connected to tools and knowledge, monitored during execution, and operated with appropriate human oversight.

**AgentOps-OS was developed to explore these challenges through a unified, full-stack AI Agent Operations platform.**


---

## 💡 Proposed Solution

**AgentOps-OS addresses the challenges of building and operating AI agent applications by bringing essential agent management, workflow orchestration, knowledge retrieval, memory, human oversight, provider integrations, and operational observability into one unified platform.**

Instead of managing these capabilities through disconnected scripts and independent services, developers can work with them through a centralized application with a modular backend and an interactive frontend.

### 🏗️ A Unified AI Agent Operations Platform

AgentOps-OS provides the following solutions to the engineering challenges identified above.

### 1. Centralized Agent Management

AgentOps-OS provides a unified environment for working with specialized AI capabilities and agent-powered tasks.

**How the platform addresses the problem:**

- Provides dedicated interfaces for AI agent interactions.
- Organizes agent-related capabilities within a common application.
- Supports analysis and report-generation use cases.
- Connects agent functionality with the platform's knowledge and workflow capabilities.
- Provides a foundation for extending agent functionality.

### 2. Visual Workflow Orchestration

The platform includes a visual workflow builder that allows users to configure and execute multi-step workflows.

**How the platform addresses the problem:**

- Provides a visual interface for workflow creation.
- Supports configurable workflow steps.
- Manages task dependencies and execution order.
- Integrates workflow tasks with available tools and AI capabilities.
- Tracks workflow execution and task results.

### 3. Structured Execution Management

AgentOps-OS provides backend services for managing workflow runs and their associated task executions.

**How the platform addresses the problem:**

- Maintains workflow execution records.
- Tracks individual task execution states.
- Provides execution results and status information.
- Supports dependency-aware task execution.
- Helps developers inspect workflow activity.

### 4. Human-in-the-Loop Control

The platform includes approval-management capabilities for introducing human review into AI-powered operations.

**How the platform addresses the problem:**

- Provides an approval-management interface.
- Supports approval-related records and decisions.
- Introduces human oversight into controlled execution scenarios.
- Separates automated processing from actions requiring human review.

### 5. Knowledge Management and Retrieval-Augmented Generation

AgentOps-OS includes a knowledge management system that allows documents to become searchable sources of information for AI applications.

**How the platform addresses the problem:**

- Supports document upload and processing.
- Provides document indexing capabilities.
- Uses embeddings for semantic retrieval.
- Integrates retrieved knowledge into AI interactions.
- Supports knowledge-grounded analysis and responses.

### 6. Persistent Agent Memory

The platform provides persistent memory capabilities to manage information associated with agent interactions.

**How the platform addresses the problem:**

- Stores memory records persistently.
- Supports memory retrieval and search.
- Provides memory inspection and editing capabilities.
- Supports memory deletion and lifecycle management.
- Connects memory functionality with agent-related operations.

### 7. Flexible AI Provider Integration

AgentOps-OS uses a provider-management architecture to support different AI model integrations.

**How the platform addresses the problem:**

- Provides a centralized provider configuration interface.
- Supports multiple provider integrations.
- Includes local model integration through Ollama.
- Supports provider connectivity testing.
- Reduces direct dependency on a single model provider.

### 8. Operational Analytics and Observability

The platform includes telemetry and observability services to record and expose operational activity.

**How the platform addresses the problem:**

- Records structured telemetry events.
- Tracks workflow and task activity.
- Records provider-related execution events.
- Provides authenticated, owner-scoped analytics endpoints.
- Exposes operational information through dashboard interfaces.

### 9. Integrated Full-Stack Application

AgentOps-OS combines its backend services, frontend interfaces, database, and AI integrations into one application.

**How the platform addresses the problem:**

- Uses FastAPI to expose modular REST APIs.
- Uses React and TypeScript for the frontend.
- Uses PostgreSQL for persistent application data.
- Uses SQLAlchemy and Alembic for database operations and migrations.
- Implements authentication and role-based access.
- Provides automated backend and frontend testing.

---

### ✅ The Outcome

AgentOps-OS brings together the engineering components required to build and operate AI-powered workflows in a single application.

Its primary focus is to make AI agent systems more:

- **Manageable** through centralized interfaces and configuration.
- **Structured** through workflow orchestration and task management.
- **Knowledge-aware** through document retrieval and persistent memory.
- **Controllable** through human approval capabilities.
- **Flexible** through AI provider abstraction and local model support.
- **Observable** through telemetry and operational analytics.
- **Maintainable** through modular backend and frontend architecture.

**The goal is to move beyond isolated AI agent implementations and explore the engineering infrastructure required to operate them as part of a complete software platform.**

---

## 🎯 Project Objectives

AgentOps-OS was developed to explore the practical engineering principles involved in designing, building, integrating, and managing modern AI agent applications.

The project combines AI engineering concepts with full-stack software development to demonstrate how agent-related capabilities can be organized into a modular and extensible platform.

### 1. AI Agent Engineering

Build practical experience with the architecture and integration of AI-powered agents.

**Objectives:**

- Develop specialized AI-powered capabilities.
- Integrate Large Language Models (LLMs) into application workflows.
- Implement reusable agent-related services.
- Explore tool integration and execution.
- Support knowledge-aware agent interactions.
- Provide a foundation for extending agent capabilities.

### 2. Workflow Orchestration

Design a structured mechanism for creating and executing multi-step AI workflows.

**Objectives:**

- Develop a visual workflow-building interface.
- Implement workflow and task management.
- Manage task dependencies and execution order.
- Integrate tools and AI capabilities into workflows.
- Track workflow execution results.
- Provide visibility into individual task states.

### 3. Retrieval-Augmented Generation (RAG)

Implement a knowledge retrieval pipeline that connects document-based information with AI applications.

**Objectives:**

- Support document ingestion and processing.
- Generate and store document embeddings.
- Implement vector-based semantic retrieval.
- Retrieve relevant knowledge for AI interactions.
- Maintain useful context for knowledge-grounded responses.
- Integrate the retrieval system with agent functionality.

### 4. Persistent Memory Management

Explore how AI applications can retain and manage useful information across interactions.

**Objectives:**

- Design persistent memory storage.
- Implement memory creation and retrieval.
- Support memory searching and inspection.
- Provide memory update and deletion operations.
- Integrate memory capabilities with agent-related services.

### 5. Human-in-the-Loop Architecture

Introduce human oversight into AI-powered operations.

**Objectives:**

- Implement approval-management functionality.
- Maintain approval-related execution records.
- Support human review and decision handling.
- Separate controlled operations from ordinary automated execution.
- Provide an interface for managing approval requests.

### 6. LLM Provider Abstraction

Build a flexible integration layer for connecting AI applications with different model providers.

**Objectives:**

- Integrate multiple supported AI providers.
- Centralize provider configuration.
- Implement provider connectivity checks.
- Support locally running models through Ollama.
- Reduce provider-specific coupling in application services.
- Allow provider integrations to be extended.

### 7. Backend Engineering

Develop a modular, maintainable backend using modern Python technologies.

**Objectives:**

- Build REST APIs using FastAPI.
- Organize application functionality into modular services.
- Use SQLAlchemy for database operations.
- Manage schema changes through Alembic migrations.
- Implement input validation and error handling.
- Apply authentication and authorization controls.
- Maintain clear separation between API, service, and data-access responsibilities.

### 8. Database and Data Management

Design a persistent data layer for application operations and AI-related information.

**Objectives:**

- Use PostgreSQL as the primary relational database.
- Integrate pgvector for vector-based knowledge retrieval.
- Model application entities and relationships.
- Maintain database schema consistency.
- Manage schema evolution through versioned migrations.
- Support ownership-aware data access.

### 9. Frontend Engineering

Develop an interactive interface for managing AI agent operations.

**Objectives:**

- Build the frontend using React and TypeScript.
- Create reusable interface components.
- Develop a centralized application dashboard.
- Implement visual workflow management.
- Provide interfaces for knowledge, memory, and provider management.
- Display execution information and operational analytics.
- Integrate frontend components with backend REST APIs.

### 10. Observability and Operational Analytics

Develop the foundation for understanding and monitoring application activity.

**Objectives:**

- Implement structured telemetry recording.
- Capture workflow and task activity.
- Record provider-related events.
- Expose operational analytics through APIs.
- Provide authenticated access to observability information.
- Support investigation of execution activity and application behavior.

### 11. Testing and Code Quality

Apply software engineering practices to improve application reliability and maintainability.

**Objectives:**

- Write automated backend tests using pytest.
- Test frontend components and application logic.
- Implement integration tests for database-backed functionality.
- Use Ruff for Python linting and formatting.
- Use mypy for static type checking.
- Use TypeScript type checking.
- Build the frontend for production.
- Maintain reproducible verification procedures.

### 12. Deployment and Development Infrastructure

Establish a consistent development environment using modern development tools.

**Objectives:**

- Use Docker and Docker Compose for database infrastructure.
- Manage Python dependencies using uv.
- Maintain environment-based configuration.
- Organize the project for local development.
- Document application startup and verification procedures.
- Maintain source control through Git and GitHub.

---

### 🚀 Overall Project Goal

The overall goal of AgentOps-OS is to demonstrate the practical integration of **AI engineering, backend development, frontend development, database architecture, workflow orchestration, and software quality practices** in one cohesive application.

The project serves as an exploration of the infrastructure and engineering principles required to build maintainable AI-powered systems beyond individual chatbot implementations.

---

## 👥 Target Users

AgentOps-OS is designed for developers, engineers, researchers, and technical teams who build, integrate, experiment with, and manage AI-powered applications.

### 1. AI Engineers and LLM Developers

For professionals working with Large Language Models, AI agents, and intelligent application architectures.

**How they can use AgentOps-OS:**
- Explore specialized AI agent implementations.
- Integrate LLM providers into application workflows.
- Experiment with local models through Ollama.
- Connect agents with external tools and knowledge sources.
- Explore persistent memory and retrieval-augmented generation.
- Monitor agent-related execution activity.

### 2. Python and Backend Developers

For developers interested in building scalable backend services for AI-powered applications.

**How they can use AgentOps-OS:**
- Explore FastAPI application architecture.
- Understand modular backend service design.
- Work with SQLAlchemy and PostgreSQL.
- Implement REST APIs and database migrations.
- Explore authentication and authorization.
- Study workflow execution and background processing concepts.

### 3. Full-Stack Developers

For developers interested in integrating AI capabilities into complete web applications.

**How they can use AgentOps-OS:**
- Explore React and TypeScript application architecture.
- Integrate frontend components with REST APIs.
- Build interactive workflow-management interfaces.
- Develop dashboard and analytics interfaces.
- Understand full-stack integration patterns.
- Work with modern frontend and backend development tools.

### 4. AI Application Development Teams

For engineering teams developing applications that require multiple AI capabilities and structured execution workflows.

**How they can use AgentOps-OS:**
- Organize AI-powered tasks and workflows.
- Connect knowledge sources with AI applications.
- Introduce human approval capabilities.
- Manage AI provider configurations.
- Inspect workflow and agent execution activity.
- Explore centralized operational management.

### 5. AI Researchers and Students

For individuals exploring practical implementations of modern AI engineering concepts.

**How they can use AgentOps-OS:**
- Study Retrieval-Augmented Generation (RAG).
- Explore agent-oriented application architecture.
- Understand vector search and embeddings.
- Experiment with persistent memory.
- Study LLM provider integration.
- Explore workflow orchestration and human oversight.

### 6. Technical Recruiters and Engineering Evaluators

For people evaluating practical software engineering and AI application development skills.

**What the project demonstrates:**
- Python backend development.
- Full-stack application engineering.
- AI and LLM integration.
- Database design and management.
- Workflow orchestration.
- Automated testing and code quality practices.
- Application observability and operational analytics.

---

### 🎯 Primary Audience

The primary audience of AgentOps-OS is developers and engineering teams interested in building and operating AI-powered applications beyond basic chatbot implementations.

---

# ✨ Key Features

AgentOps-OS combines AI agent capabilities, workflow orchestration, knowledge management, persistent memory, human oversight, provider integrations, and operational observability into one unified application.

The following sections highlight the major capabilities of the platform.

---

## 📊 1. Centralized Dashboard

<!-- Screenshot: docs/screenshots/dashboard.png -->

The AgentOps-OS dashboard provides a centralized interface for accessing important platform information and operational functionality.

**Key Capabilities:**
- Centralized application workspace.
- Workflow activity overview.
- Agent-related information.
- Operational metrics and summaries.
- Navigation to major platform features.
- Access to workflow and system-management interfaces.

**Engineering Implementation:**

The dashboard integrates frontend components with backend APIs to retrieve and present application-level operational information.

---

## 🔄 2. Visual Workflow Builder

<!-- Screenshot: docs/screenshots/workflow-builder.png -->

AgentOps-OS provides a visual workflow-building interface for designing structured, multi-step execution workflows.

Instead of managing every operation through manually written sequences, users can configure workflow steps through an interactive visual interface.

**Key Capabilities:**
- Visual workflow creation.
- Configurable workflow nodes.
- Workflow step management.
- Task dependency configuration.
- Structured workflow definitions.
- Integration with supported execution capabilities.

**Engineering Implementation:**

The workflow interface communicates with backend workflow services responsible for managing workflow definitions, tasks, and execution dependencies.

---

## ⚙️ 3. Workflow Execution Engine

<!-- Screenshot: docs/screenshots/workflow-execution.png -->

The workflow execution engine manages the execution of configured workflows and their associated tasks.

It provides a structured mechanism for executing multi-step operations while maintaining information about individual tasks and workflow runs.

**Key Capabilities:**
- Workflow execution management.
- Dependency-aware task execution.
- Task status tracking.
- Execution result management.
- Workflow run history.
- Execution error visibility.

**Engineering Implementation:**

The backend provides workflow and task execution services, persistent execution records, and APIs for accessing workflow activity and results.

---

## 🤖 4. Specialized AI Agent Capabilities

<!-- Screenshot: docs/screenshots/agent-analysis.png -->

AgentOps-OS provides specialized AI capabilities for tasks involving knowledge analysis and report generation.

These capabilities allow AI-powered operations to be integrated into the wider workflow and knowledge-management environment.

**Key Capabilities:**
- AI-powered analysis.
- Knowledge-supported interactions.
- Structured report generation.
- Integration with supported LLM providers.
- Access to relevant application knowledge sources.
- Agent-related execution management.

**Engineering Implementation:**

Agent functionality is integrated with backend services responsible for provider interaction, knowledge retrieval, and application-level execution.

See the [Agent System](#-agent-system) section for more details.

---

## 🧑‍⚖️ 5. Human-in-the-Loop Approval Management

<!-- Screenshot: docs/screenshots/approval-management.png -->

AgentOps-OS includes approval-management functionality to introduce human oversight into AI-powered operations.

This allows approval-related activities to be represented and managed through a dedicated application interface.

**Key Capabilities:**
- Approval-management interface.
- Approval-related records.
- Human review and decision handling.
- Approval status visibility.
- Integration with platform authorization mechanisms.

**Engineering Implementation:**

The backend provides approval-related application services and persistent records, while the frontend provides the interface for reviewing approval information.

---

## 📚 6. Knowledge Management

<!-- Screenshot: docs/screenshots/knowledge-base.png -->

The Knowledge Management module provides a centralized interface for managing documents used by the platform's knowledge retrieval capabilities.

Documents can be processed and indexed to make their content available to supported knowledge-aware AI operations.

**Key Capabilities:**
- Document upload.
- Document management.
- Document processing and indexing.
- Knowledge source organization.
- Integration with semantic retrieval.
- Document-based AI interactions.

**Engineering Implementation:**

The knowledge pipeline integrates document processing, embedding generation, vector storage, and retrieval services.

---

## 🔍 7. Retrieval-Augmented Generation (RAG)

<!-- Screenshot: docs/screenshots/knowledge-search.png -->

AgentOps-OS incorporates Retrieval-Augmented Generation to connect AI interactions with information stored in indexed knowledge sources.

Instead of relying only on information contained in a model's parameters, the application can retrieve relevant document content and provide it as additional context.

**Key Capabilities:**
- Document embedding generation.
- Vector-based semantic retrieval.
- Knowledge search.
- Retrieval of relevant document content.
- Context integration for AI interactions.
- Source-aware knowledge responses.

**Engineering Implementation:**

The RAG implementation uses document-processing services, embedding integration, and PostgreSQL with pgvector for vector-based retrieval.

---

## 🧠 8. Persistent Agent Memory

<!-- Screenshot: docs/screenshots/agent-memory.png -->

AgentOps-OS provides persistent memory-management capabilities for storing and managing information associated with agent-related interactions.

Memory records can be inspected and managed through a dedicated application interface.

**Key Capabilities:**
- Persistent memory storage.
- Memory creation and retrieval.
- Memory search.
- Memory inspection.
- Memory editing.
- Memory deletion and lifecycle management.

**Engineering Implementation:**

The memory functionality uses backend services and persistent database records to support memory-related operations.

---

## 🔌 9. AI Provider Management

<!-- Screenshot: docs/screenshots/provider-settings.png -->

AgentOps-OS provides a centralized interface for configuring supported AI providers.

The provider-management architecture helps separate model-provider integration from application-level agent functionality.

**Key Capabilities:**
- Provider configuration.
- Supported provider integrations.
- Provider connectivity testing.
- Local model integration through Ollama.
- Model configuration management.
- Provider-related execution information.

**Engineering Implementation:**

A provider abstraction layer connects application services with supported model integrations.

Ollama provides an option for running compatible models locally without depending on a paid hosted model API.

---

## 📈 10. Analytics and Observability

<!-- Screenshot: docs/screenshots/analytics.png -->

AgentOps-OS includes operational telemetry and analytics capabilities for inspecting activity across different parts of the platform.

The observability layer provides structured information about application execution and provider-related operations.

**Key Capabilities:**
- Workflow activity analytics.
- Agent-related analytics.
- Provider activity information.
- Execution telemetry.
- Operational summaries.
- Owner-scoped observability endpoints.

**Engineering Implementation:**

The backend includes telemetry recording services and authenticated observability APIs for retrieving operational information.

---

## 🔐 11. Authentication and Account Management

<!-- Screenshot: docs/screenshots/authentication.png -->

AgentOps-OS provides account authentication and registration functionality for controlling access to the application.

The registration flow supports email-based OTP verification and account creation with a default operator role.

**Key Capabilities:**
- Public account registration.
- Email OTP verification.
- User authentication.
- Default operator-role assignment.
- Administrator account management.
- Protected application access.

**Engineering Implementation:**

Authentication functionality is implemented through backend authentication services, database-backed account records, email verification, and authorization mechanisms.

---

### 🚀 Unified Platform Experience

These capabilities work together to provide a common environment for building and managing AI-powered operations.

AgentOps-OS brings together:

**AI Agents • Workflow Orchestration • Knowledge Retrieval • Persistent Memory • Human Oversight • Provider Management • Observability**

---

# 🤖 Agent System

The Agent System is one of the core AI engineering components of AgentOps-OS.

Rather than treating every AI interaction as a generic chatbot request, the platform provides specialized AI capabilities for different types of tasks.

The current application includes analysis and report-generation capabilities that can work with configured LLM providers and available knowledge sources.

## 🧩 Specialized Agent Capabilities

### 1. Analysis Agent

<!-- Screenshot: docs/screenshots/agent-analysis.png -->

The Analysis Agent focuses on interpreting user requests and producing analytical responses using available AI capabilities and relevant knowledge context.

**Responsibilities:**
- Analyze user-provided tasks and questions.
- Process relevant contextual information.
- Interact with configured AI providers.
- Use available knowledge sources where applicable.
- Produce structured analytical outputs.

**Example Use Cases:**
- Analyzing information from indexed knowledge documents.
- Answering questions using retrieved context.
- Extracting meaningful information from available sources.
- Supporting knowledge-based investigation tasks.

### 2. Report Agent

<!-- Screenshot: docs/screenshots/agent-report.png -->

The Report Agent focuses on generating structured reports from provided information and available contextual knowledge.

**Responsibilities:**
- Organize relevant information.
- Generate structured report content.
- Present findings in a readable format.
- Use available knowledge context.
- Produce report-oriented outputs.

**Example Use Cases:**
- Generating knowledge-based reports.
- Organizing findings into structured sections.
- Preparing summaries from available information.
- Presenting analytical results in report format.

---

## 🔄 Agent Execution and Collaboration

AgentOps-OS brings agent capabilities into a broader workflow and application environment.

The platform's workflow and backend services provide the foundation for organizing tasks that use different application capabilities.

### Conceptual Execution Flow

```mermaid
flowchart TD
    A([User Request])
    B[Application Interface]
    C[Backend API]
    D[Task and Workflow Services]
    E{Required Capability}

    F[Analysis Agent]
    G[Report Agent]
    H[Knowledge Retrieval]
    I[Configured LLM Provider]
    J[Structured Output]
    K[Execution Records and Telemetry]

    A --> B
    B --> C
    C --> D
    D --> E

    E --> F
    E --> G

    F --> H
    G --> H

    H --> I
    I --> J

    J --> K
    K --> B
```

*Note: This diagram illustrates the conceptual integration of the platform's agent, workflow, knowledge, and provider capabilities. It does not claim autonomous agent-to-agent communication or an independently verified multi-agent handoff.*

---

## 🧠 Agent Context and Knowledge Integration

AI agent functionality can be enhanced through the platform's knowledge-management capabilities.

The knowledge retrieval pipeline helps provide relevant information to supported AI operations.

The process can be represented as:

1. Documents are uploaded to the knowledge system.
2. Document-processing services prepare the content.
3. Embeddings are generated.
4. Vector representations are stored using pgvector.
5. Relevant content is retrieved through semantic search.
6. Retrieved context can be supplied to supported AI interactions.
7. The agent produces an output using the available context.

---

## 🔌 LLM Provider Integration

Agent-related functionality communicates with configured model providers through the platform's provider-management architecture.

This approach helps separate agent-level application logic from provider-specific integration details.

Supported integration capabilities include:

- Configured AI provider connections.
- Provider configuration management.
- Model selection and configuration.
- Local model integration through Ollama.
- Provider connectivity testing.

---

## 🏗️ Agent System Engineering Principles

The agent architecture explores several important AI engineering principles:

| Principle | Purpose |
|---|---|
| Specialization | Organize AI capabilities around different task types |
| Modularity | Separate agent functionality from unrelated application services |
| Provider Abstraction | Reduce direct dependency on a single model provider |
| Knowledge Integration | Supply relevant retrieved information to AI operations |
| Workflow Integration | Organize AI-related tasks within structured workflows |
| Persistent Storage | Maintain application and execution records |
| Observability | Record operational activity for inspection |

### 🚀 Design Philosophy

**A useful AI agent system requires more than a model capable of generating responses. It requires an organized execution environment, knowledge integration, provider management, persistent application data, and appropriate operational controls.**

AgentOps-OS explores these engineering principles by integrating specialized AI capabilities into a broader full-stack operations platform.

---

# 🔄 Workflow Orchestration

Workflow Orchestration is a core component of AgentOps-OS. It provides a structured way to design, configure, execute, and monitor multi-step workflows through a visual interface and dedicated backend services.

Instead of treating every AI operation as an isolated request, AgentOps-OS organizes tasks into workflows that can be executed according to their configured dependencies.

## 🎨 1. Visual Workflow Builder

<!-- Screenshot: docs/screenshots/workflow-builder.png -->

The visual workflow builder provides an interactive environment for creating and configuring workflows.

Users can organize workflow steps using a visual canvas and configure the operations that make up an execution.

**Key Capabilities:**
- Visual workflow creation.
- Workflow node management.
- Configurable workflow steps.
- Start and End nodes.
- Tool-based task configuration.
- Workflow definition management.
- Dependency-aware workflow design.

## ⚙️ 2. Workflow Execution Engine

<!-- Screenshot: docs/screenshots/workflow-execution.png -->

The workflow execution engine is responsible for coordinating the execution of configured workflow tasks.

It processes workflow definitions and manages the associated task executions while maintaining execution information.

**Key Capabilities:**
- Workflow run creation.
- Structured task execution.
- Dependency-aware execution ordering.
- Individual task state tracking.
- Task result management.
- Workflow execution status.
- Persistent execution records.

## 🔗 3. Task Dependencies

Workflow tasks may depend on the successful completion of preceding tasks.

AgentOps-OS uses task dependency information to organize execution order and manage relationships between workflow steps.

**Key Capabilities:**
- Define relationships between workflow tasks.
- Represent execution dependencies.
- Respect configured task ordering.
- Manage dependent task execution.
- Maintain task-level execution information.

This approach helps organize complex operations into smaller, manageable execution units.

## 📊 4. Workflow Monitoring

<!-- Screenshot: docs/screenshots/workflow-execution.png -->

The platform provides execution information that helps users inspect workflow activity and individual task results.

**Key Capabilities:**
- Workflow run information.
- Execution status visibility.
- Task-level results.
- Execution history information.
- Error and failure information where recorded.
- Integration with operational telemetry.

## 🧪 5. Example Workflow Execution

A basic workflow can be represented using the following structure:

```mermaid
flowchart TD
    A([Start])
    B[Text Statistics Tool]
    C([End])

    A --> B
    B --> C
```

**Example execution:**

1. A workflow is created using the visual builder.
2. A Start node initiates the workflow.
3. The `text_statistics` tool processes the configured input.
4. The tool returns its execution result.
5. The End node completes the workflow.

This Start → Text Statistics → End workflow was successfully executed during application validation.

### Example Execution Output

The demonstrated execution returned structured statistics including:

| Metric | Result |
|---|---:|
| Line Count | 1 |
| Word Count | 4 |
| Character Count | 32 |

*These values represent one demonstrated test execution, not general workflow performance benchmarks.*

## 🏗️ Workflow Orchestration Architecture

The following diagram illustrates the main conceptual components involved in workflow execution.

```mermaid
flowchart TD
    A[User]
    B[React Workflow Builder]
    C[FastAPI Backend]
    D[Workflow Services]
    E[Dependency Management]
    F[Task Execution]
    G[Tool or Agent Capability]
    H[(PostgreSQL)]
    I[Execution Results]
    J[Workflow Monitoring]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    I --> J
    H --> J
```

*Architecture overview: this diagram represents the workflow execution components and their relationships, rather than a low-level sequence diagram of every internal function.*

## 💡 Engineering Value

The workflow orchestration system demonstrates several practical software engineering concepts:

- Visual workflow modeling.
- Dependency-aware execution.
- Modular task processing.
- Tool integration.
- Persistent execution management.
- Backend and frontend integration.
- Operational monitoring.

**The objective is to provide a structured execution environment in which individual tools and AI capabilities can participate in larger, organized workflows.**

---

# 🧑‍⚖️ Human-in-the-Loop (HITL)

Human-in-the-Loop (HITL) is an important design principle for AI-powered applications where certain operations require human review or decision-making.

AgentOps-OS includes approval-management functionality to introduce human oversight into AI-related application operations.

Instead of treating every operation as an entirely automated activity, the platform provides mechanisms for representing and managing approval-related records.

## 🎯 Why Human Oversight Matters

AI-powered systems can perform complex tasks, interact with tools, and generate actions based on user requests.

However, some operations may require additional review before they are considered appropriate to proceed.

Human oversight helps introduce an additional layer of control into these application workflows.

**Important Considerations:**
- Maintaining human visibility into approval-related activities.
- Recording approval requests and their associated information.
- Supporting review and decision handling.
- Maintaining approval status information.
- Providing appropriate access to approval-management functionality.

## 📋 1. Approval Management Interface

<!-- Screenshot: docs/screenshots/approval-management.png -->

AgentOps-OS provides a dedicated interface for accessing approval-related information.

**Key Capabilities:**
- Approval-management view.
- Approval request information.
- Approval status visibility.
- Human review interface.
- Approval-related decision management.

## 🔎 2. Approval Review

The approval-management functionality provides a foundation for reviewing operations that require human consideration.

The review process is intended to make approval-related information accessible to authorized users.

**Review Considerations:**
- Inspect the associated approval information.
- Understand the operation requiring review.
- Review the available context.
- Record the appropriate decision through supported approval functionality.

## ✅ 3. Approval Decisions

AgentOps-OS includes backend approval-related functionality for managing human decisions.

The application separates approval management from ordinary agent and workflow interactions so that approval-related operations can be handled through dedicated application services.

**Key Capabilities:**
- Approval-related records.
- Decision management.
- Approval status tracking.
- Authenticated application access.
- Persistent approval information.

## 🔄 4. Conceptual Human Approval Flow

The following diagram illustrates the intended human-review process at a conceptual level.

```mermaid
flowchart TD
    A([Application Operation])
    B[Approval Required]
    C[Create Approval Request]
    D[Human Review]
    E{Decision}
    F[Approved]
    G[Rejected]
    H[Record Decision]
    I([Continue or Close Operation])

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> H
    H --> I
```

*This diagram describes the approval-management concept. It should not be interpreted as proof that every workflow automatically pauses and resumes based on approval decisions.*

## 🔐 5. Access Control and Oversight

Human review functionality is part of the broader authenticated application environment.

AgentOps-OS also implements authentication and authorization mechanisms to control access to application functionality and protected resources.

## 🧪 Verification Status

The approval-management interface and its empty-state behavior have been inspected during frontend validation.

The complete end-to-end sequence of creating an approval request, recording a decision, and verifying its effect on workflow execution remains to be demonstrated.

This distinction is important: the presence of approval-related functionality does not by itself establish that every possible approval scenario has been fully validated.

## 💡 Engineering Value

The Human-in-the-Loop implementation explores:

- Human oversight in AI-powered applications.
- Approval-related backend services.
- Persistent approval records.
- Decision-management interfaces.
- Authentication and controlled access.
- Integration considerations for automated operations.

**The goal is to make AI-powered operations more manageable by introducing human review and decision-making capabilities where required.**

---

# 📚 Knowledge Management & Retrieval-Augmented Generation (RAG)

AgentOps-OS includes a Knowledge Management system that connects document-based information with AI-powered application capabilities.

It implements a Retrieval-Augmented Generation (RAG) approach in which relevant information is retrieved from indexed knowledge sources and supplied as additional context to supported AI interactions.

Rather than relying exclusively on a language model's pre-existing knowledge, RAG allows applications to incorporate information from their own document collections.

## 📄 1. Document Ingestion

<!-- Screenshot: docs/screenshots/knowledge-base.png -->

The Knowledge Management interface provides a centralized environment for uploading and managing documents.

Documents are processed through the backend knowledge pipeline to prepare their content for retrieval.

**Key Capabilities:**
- Document upload.
- Knowledge document management.
- Document processing.
- Content preparation for indexing.
- Knowledge source organization.
- Integration with downstream retrieval operations.

## ⚙️ 2. Document Processing and Indexing

After document ingestion, the knowledge pipeline prepares document content for retrieval.

The indexing process transforms document information into representations that can be searched using semantic similarity.

**Key Capabilities:**
- Document content processing.
- Text preparation.
- Embedding generation.
- Vector representation management.
- Persistent knowledge indexing.

## 🧬 3. Embedding Generation

Embeddings represent textual information as numerical vectors that capture semantic characteristics.

AgentOps-OS integrates embedding functionality into its knowledge retrieval architecture.

The local embedding model used during development includes:

- `embeddinggemma:latest` through Ollama.

Embedding generation makes it possible to retrieve information based on semantic similarity rather than depending exclusively on exact keyword matches.

## 🗄️ 4. Vector Storage with PostgreSQL and pgvector

AgentOps-OS uses PostgreSQL as its primary database and pgvector for vector-based knowledge retrieval.

The combination provides relational persistence alongside vector operations.

**Key Capabilities:**
- Persistent knowledge records.
- Vector representation storage.
- Semantic similarity search.
- Integration with application data.
- Database-backed retrieval operations.

## 🔍 5. Semantic Knowledge Retrieval

<!-- Screenshot: docs/screenshots/knowledge-search.png -->

The knowledge retrieval functionality allows users and supported AI operations to search indexed information.

Instead of requiring an exact textual match, semantic retrieval helps identify relevant content based on the meaning of a query.

**Key Capabilities:**
- Knowledge search.
- Semantic retrieval.
- Relevant content selection.
- Retrieval of indexed document information.
- Knowledge integration with AI interactions.
- Citation information for retrieved sources.

## 🤖 6. Knowledge-Grounded AI Interactions

Retrieved knowledge can be supplied as context to supported AI capabilities.

This helps connect the platform's document repository with its Analysis Agent and Report Agent functionality.

**Example Use Cases:**
- Asking questions about indexed documents.
- Analyzing information available in knowledge sources.
- Generating reports using retrieved information.
- Producing responses supported by relevant source content.

## 🔄 7. RAG Pipeline Architecture

The following diagram illustrates the knowledge ingestion and retrieval pipeline.

```mermaid
flowchart TD
    A([Document Upload])
    B[Document Processing]
    C[Text Preparation]
    D[Embedding Generation]
    E[(PostgreSQL + pgvector)]
    F([User Knowledge Query])
    G[Query Embedding]
    H[Semantic Retrieval]
    I[Relevant Knowledge]
    J[AI Agent]
    K[Configured LLM Provider]
    L([Knowledge-Grounded Response])

    A --> B
    B --> C
    C --> D
    D --> E

    F --> G
    G --> H
    E --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

*The diagram presents the logical RAG pipeline. Document ingestion and query processing are separate operations that meet at the retrieval stage.*

## 🧪 8. Demonstrated Knowledge Workflow

The knowledge functionality has been exercised through the following application-level workflow:

1. Upload a TXT document through the Knowledge Management interface.
2. Process and index the uploaded document.
3. Search the indexed knowledge.
4. Retrieve relevant information with citation details.
5. Use the knowledge source in an Analysis Agent interaction.
6. Generate a knowledge-supported report through the Report Agent.

The knowledge workflow was demonstrated successfully during frontend validation.

## 🧠 9. Example Application Scenario

Consider a technical document containing information about PostgreSQL.

A user can upload the document into the knowledge system and subsequently ask a question related to its contents.

The retrieval pipeline identifies relevant information from the indexed document and makes it available to a supported AI interaction.

The Analysis Agent can then produce an answer based on the retrieved context, while the Report Agent can organize relevant findings into a structured report.

## 🏗️ 10. Engineering Components

| Component | Responsibility |
|---|---|
| Document Ingestion | Accepts documents into the knowledge system |
| Document Processing | Prepares document content |
| Embedding Integration | Converts textual content into vector representations |
| Ollama | Provides local embedding-model integration |
| PostgreSQL | Persistent application and knowledge data |
| pgvector | Vector storage and semantic retrieval |
| Retrieval Services | Retrieve relevant knowledge information |
| AI Provider Integration | Supports knowledge-aware AI interactions |
| Frontend Knowledge Interface | Provides document and search management |

## 💡 Engineering Value

The Knowledge Management and RAG implementation demonstrates practical experience with:

- Document ingestion and processing.
- Embedding generation.
- Vector databases.
- Semantic search.
- Retrieval-Augmented Generation.
- Knowledge-grounded AI interactions.
- Local embedding-model integration.
- Database-backed AI application development.

**The objective is to connect AI applications with external knowledge sources so that their interactions can use relevant, application-specific information rather than depending only on the model's pre-existing knowledge.**

---

# 🧠 Agent Memory & Persistent Context Management

AgentOps-OS includes a persistent memory-management system designed to store, retrieve, search, and manage information associated with AI application interactions.

Memory management provides an additional layer of context for AI-powered applications by allowing relevant information to be maintained beyond an individual interaction.

The platform provides a dedicated interface and backend services for managing memory records and their lifecycle.

## 💾 1. Persistent Agent Memory

<!-- Screenshot: docs/screenshots/agent-memory.png -->

The Agent Memory module provides an interface for accessing and managing persistent memory records.

Unlike temporary request context, persistent memory records are stored in the application's database and can be accessed through supported memory operations.

**Key Capabilities:**
- Create memory records.
- Retrieve stored memories.
- Inspect individual memory records.
- Search existing memories.
- Edit memory information.
- Delete individual memories.
- Manage memory lifecycle operations.

## 🔎 2. Memory Retrieval and Search

AgentOps-OS provides memory retrieval and search functionality to help locate previously stored information.

**Key Capabilities:**
- Search stored memory records.
- Retrieve relevant memory information.
- Inspect individual memory details.
- Access previously stored context.
- Manage memory records through application interfaces.

Memory retrieval provides the foundation for incorporating previously stored information into supported AI application operations.

## 🗂️ 3. Memory Management

<!-- Screenshot: docs/screenshots/memory-management.png -->

The platform provides memory-management operations through a dedicated application interface.

**Supported Operations:**

| Operation | Description |
|---|---|
| Create | Store a new memory record |
| List | View available memory records |
| Retrieve | Access an individual memory |
| Search | Search stored memory information |
| Update | Modify an existing memory |
| Delete | Remove an individual memory |
| Purge | Perform supported memory lifecycle cleanup |

These operations provide control over how persistent memory records are maintained.

## 🔄 4. Memory Lifecycle

The following diagram illustrates the logical lifecycle of a memory record.

```mermaid
flowchart TD
    A([New Information])
    B[Create Memory]
    C[(Persistent Memory Storage)]
    D[Retrieve Memory]
    E[Search Memories]
    F[Inspect Memory]
    G[Update Memory]
    H[Delete Memory]
    I[Purge Operation]

    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    E --> F
    F --> G
    F --> H
    C --> I
```

*This diagram illustrates the supported memory-management operations and their logical relationships.*

## 💬 5. Conversation Context and Memory

Persistent memory and conversation history represent related but distinct concepts.

- **Conversation Context:** Information associated with an ongoing interaction.
- **Persistent Memory:** Information stored for retrieval and management beyond an individual request.

AgentOps-OS provides persistent memory-management functionality as part of its broader AI application architecture.

Memory capabilities can support applications that need to retrieve previously stored information and incorporate relevant context into subsequent operations.

## 🏗️ 6. Memory System Architecture

The memory-management functionality integrates the frontend, backend services, and persistent database layer.

```mermaid
flowchart TD
    A([User])
    B[React Memory Interface]
    C[FastAPI Backend]
    D[Memory Services]
    E[Memory Operations]
    F[(PostgreSQL Database)]
    G[Retrieved Memory Information]

    A --> B
    B --> C
    C --> D
    D --> E
    E <--> F
    F --> G
    G --> B
```

## 🧪 7. Demonstrated Memory Operations

The memory-management functionality was exercised during frontend validation.

The following operations were tested:

- Memory creation.
- Memory listing.
- Individual memory inspection.
- Memory search.
- Memory editing.
- Individual memory deletion.
- Memory purge operations.

These checks demonstrated the corresponding memory-management interfaces and operations.

## 🏗️ 8. Engineering Components

| Component | Responsibility |
|---|---|
| React Memory Interface | Provides memory-management functionality |
| FastAPI APIs | Exposes memory operations |
| Memory Services | Implements memory-related application logic |
| PostgreSQL | Provides persistent storage |
| Search Functionality | Locates stored memory records |
| Lifecycle Operations | Supports memory updates and removal |

## 💡 Engineering Value

The Agent Memory implementation demonstrates practical experience with:

- Persistent data management.
- Memory lifecycle operations.
- Backend service design.
- Search and retrieval functionality.
- Database-backed application features.
- Frontend and backend integration.
- Context-management considerations for AI applications.

**The objective is to provide a manageable persistent-memory layer that can support context-aware AI application functionality.**

---

# 🔌 AI Provider Management & LLM Integration

AgentOps-OS includes an AI Provider Management system designed to configure, integrate, and manage supported Large Language Model (LLM) providers.

Different AI providers have different configuration requirements, model options, connectivity characteristics, and operational behavior.

The platform uses a provider-management architecture to organize these integrations and reduce direct dependency on a single model provider.

## 🧩 1. Provider Abstraction

The provider-management architecture separates AI provider integration from application-level functionality.

This helps backend services interact with supported model providers through an organized integration layer.

**Key Capabilities:**
- Centralized provider configuration.
- Multiple supported provider integrations.
- Model configuration management.
- Provider connectivity testing.
- Provider-related execution information.
- Integration with AI-powered application capabilities.

## ⚙️ 2. Provider Configuration

<!-- Screenshot: docs/screenshots/provider-settings.png -->

AgentOps-OS provides a settings interface for managing supported AI providers.

Users can access provider-related configuration and test connectivity through the application.

**Key Capabilities:**
- Provider management interface.
- Provider configuration.
- Model selection and configuration.
- Connectivity testing.
- Provider status information.
- Local model configuration.

## 🦙 3. Local LLM Integration with Ollama

<!-- Screenshot: docs/screenshots/ollama-configuration.png -->

AgentOps-OS supports local model integration through Ollama.

Ollama provides a way to run compatible language models on a local machine without depending on a paid hosted model API.

This allows developers to experiment with AI-powered application functionality using locally running models.

**Key Capabilities:**
- Local Ollama integration.
- Connection to a running Ollama service.
- Local model configuration.
- Provider connectivity testing.
- Integration with supported LLM functionality.
- Local model experimentation.

## 🤖 4. Models Used During Development

The following locally running models were used during development and validation.

| Model | Purpose | Runtime |
|---|---|---|
| `qwen3.5:0.8b` | Local language-model integration | Ollama |
| `embeddinggemma:latest` | Text embedding generation | Ollama |

**Why local models?**

Local models provide an option for experimentation without requiring a paid hosted inference API.

Actual performance depends on the model, available hardware, configuration, and workload.

## 🔄 5. Provider Interaction Flow

The following diagram illustrates the logical provider integration flow.

```mermaid
flowchart TD
    A([User Request])
    B[Frontend Application]
    C[FastAPI Backend]
    D[Application or Agent Service]
    E[Provider Abstraction]
    F{Configured Provider}
    G[Ollama Local Runtime]
    H[Supported Hosted Provider]
    I[Model Execution]
    J[Generated Response]
    K[Application Result]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    G --> I
    H --> I
    I --> J
    J --> K
    K --> B
```

*This diagram represents the logical provider integration architecture. The actual execution path depends on the selected provider and application capability.*

## 🧪 6. Provider Connectivity Testing

AgentOps-OS provides provider connectivity-testing functionality to help validate configured integrations.

Provider validation can help identify configuration or connection problems before using a provider in application operations.

**Validation Areas:**
- Provider configuration.
- Service connectivity.
- Model availability.
- Provider response handling.
- Local runtime integration.

## ✅ 7. Demonstrated Ollama Integration

The local Ollama provider was successfully configured and tested during application validation.

The demonstrated configuration included:

| Setting | Value |
|---|---|
| Provider | Ollama |
| Runtime URL | `http://localhost:11434` |
| Language Model | `qwen3.5:0.8b` |
| Embedding Model | `embeddinggemma:latest` |
| Runtime Type | Local |

The provider connectivity test succeeded using the configured Ollama model.

The embedding model was used separately for the local knowledge-embedding workflow.

## 🏗️ 8. Provider Management Architecture

The provider-management system can be understood through the following conceptual component structure.

```mermaid
flowchart TD
    A[Frontend Settings]
    B[FastAPI Provider APIs]
    C[Provider Management Services]
    D[Provider Configuration]
    E[Provider Integration Layer]
    F[Ollama]
    G[Hosted AI Providers]
    H[Model Execution]
    I[Provider Result]
    J[Application Services]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> H
    H --> I
    I --> J
```

## 🔐 9. Configuration and Security

AI provider configuration may involve sensitive information such as API credentials and connection settings.

AgentOps-OS uses environment-based configuration and application security mechanisms to support controlled configuration management.

**Important Practices:**
- Keep API credentials outside source code.
- Use environment variables for sensitive settings.
- Do not commit private provider credentials.
- Restrict access to protected configuration operations.
- Use local models when local inference is appropriate.

## 💡 10. Engineering Value

The AI Provider Management implementation demonstrates practical experience with:

- LLM provider integration.
- Provider abstraction.
- Local model deployment and connectivity.
- Model configuration.
- Provider testing.
- Environment-based configuration.
- Integration of LLMs into backend services.
- Local embedding-model integration.

**The objective is to make AI provider integrations more manageable and extensible while allowing developers to experiment with both local and hosted model options.**

---

# 📊 Analytics & Observability

AgentOps-OS includes an observability and analytics layer designed to provide visibility into application activity, workflow execution, agent operations, and AI provider interactions.

The observability infrastructure records structured telemetry events and exposes operational information through authenticated backend APIs.

The objective is to make AI-powered application activity easier to inspect, understand, and investigate.

## 📈 1. Operational Analytics Dashboard

<!-- Screenshot: docs/screenshots/analytics.png -->

The Analytics interface provides access to operational information collected by the platform.

It connects frontend dashboard components with backend observability APIs to retrieve available analytics information.

**Key Capabilities:**
- Operational overview.
- Workflow activity information.
- Agent-related analytics.
- Provider activity information.
- Execution-related information.
- Analytics API integration.

## 📡 2. Structured Telemetry Recording

AgentOps-OS includes a centralized telemetry-recording mechanism for capturing structured application events.

The backend provides a `TelemetryRecorder` service that records telemetry information through the application's instrumentation layer.

**Key Capabilities:**
- Structured telemetry event recording.
- Persistent telemetry records.
- Context-local instrumentation.
- Workflow-related event tracking.
- Task execution telemetry.
- AI provider attempt tracking.

The telemetry infrastructure provides a foundation for understanding activity across different application components.

## 🔄 3. Workflow and Task Analytics

Workflow execution generates information that can help developers understand how application workflows behave.

AgentOps-OS incorporates workflow and task-related telemetry into its observability architecture.

**Key Capabilities:**
- Workflow execution information.
- Task-related operational events.
- Execution status information.
- Workflow activity analytics.
- Task-level operational visibility.

These capabilities help connect workflow execution with the broader observability layer.

## 🤖 4. AI Provider and LLM Analytics

AI provider interactions are important operational events in an LLM-powered application.

AgentOps-OS includes provider-attempt telemetry and LLM-related analytics functionality.

**Key Capabilities:**
- Provider attempt recording.
- LLM-related telemetry.
- Provider activity information.
- Provider analytics APIs.
- Integration with the provider-management architecture.

This provides a foundation for inspecting AI provider activity across supported application operations.

## 🧩 5. Agent Analytics

The observability backend also provides agent-related analytics functionality.

This helps organize operational information associated with agent activity and expose it through the platform's analytics interfaces.

**Key Capabilities:**
- Agent-related analytics.
- Agent activity information.
- Integration with telemetry records.
- Authenticated analytics access.

## 🔐 6. Authenticated Observability APIs

AgentOps-OS exposes observability information through authenticated, owner-scoped backend endpoints.

The API layer provides dedicated access to different categories of operational information.

**Implemented API categories:**

| API Category | Purpose |
|---|---|
| Overview | Provides a consolidated operational overview |
| Providers | Exposes provider-related analytics |
| Agents | Exposes agent-related analytics |
| Workflows | Exposes workflow-related analytics |

Owner-scoped access helps ensure that authenticated users retrieve information within their permitted application ownership context.

## 🏗️ 7. Observability Architecture

The following diagram illustrates the main components of the observability infrastructure.

```mermaid
flowchart TD
    A[Workflow Execution]
    B[Task Execution]
    C[AI Provider Attempts]
    D[LLM Operations]

    E[Application Instrumentation]
    F[TelemetryRecorder]
    G[(TelemetryEvent Storage)]
    H[Observability APIs]
    I[React Analytics Interface]

    A --> E
    B --> E
    C --> E
    D --> E

    E --> F
    F --> G
    G --> H
    H --> I
```

*Architecture overview: the diagram represents the telemetry collection and retrieval flow implemented by the platform.*

## 🗄️ 8. Telemetry Persistence

AgentOps-OS uses PostgreSQL for persistent application data.

The observability implementation introduces a `TelemetryEvent` model and a corresponding database migration to maintain telemetry records.

**Implementation Components:**

| Component | Responsibility |
|---|---|
| TelemetryEvent | Represents persistent telemetry records |
| TelemetryRecorder | Records structured telemetry events |
| Context-local Instrumentation | Supports contextual event recording |
| Provider Instrumentation | Captures provider attempt telemetry |
| Analytics Services | Organizes operational analytics |
| Observability APIs | Exposes analytics information |
| React Analytics Interface | Presents operational information |

## 🧪 9. Verification and Testing

The observability functionality was validated through backend and frontend checks.

The following areas were exercised:

- Observability API availability.
- Overview endpoint responses.
- Provider analytics endpoint responses.
- Agent analytics endpoint responses.
- Workflow analytics endpoint responses.
- Frontend analytics API integration.
- Analytics interface rendering.
- Empty-state handling when analytics data is unavailable.

**Verification Note:**

The analytics endpoints were successfully accessed during frontend validation. Some analytics interfaces displayed empty states because corresponding event data was not populated for those views.

The existence of an analytics endpoint does not automatically mean that every dashboard metric has been demonstrated with populated production-like data.

## 💡 Engineering Value

The Analytics and Observability implementation demonstrates practical experience with:

- Structured telemetry.
- Database-backed event recording.
- Application instrumentation.
- Workflow and task monitoring.
- LLM provider telemetry.
- Authenticated analytics APIs.
- Owner-scoped data access.
- Frontend and backend analytics integration.

**The objective is to make AI-powered application operations more transparent and easier to inspect through structured telemetry and centralized observability.**

---

# 🔐 Authentication & Security

AgentOps-OS includes an authentication and access-control system designed to protect application functionality and manage user access.

The platform supports public self-service registration, email-based OTP verification, account authentication, and role-based access.

Its authentication architecture separates ordinary operator registration from administrator account management.

## 👤 1. Public Self-Service Registration

<!-- Screenshot: docs/screenshots/registration.png -->

AgentOps-OS supports public account registration without requiring an administrator invitation.

A visitor can begin the registration process by providing an email address and completing the required verification steps.

**Registration Capabilities:**
- Public self-service signup.
- Email address submission.
- Six-digit OTP generation and verification.
- Account creation after successful verification.
- Automatic assignment of the default `operator` role.
- Automatic sign-in following successful registration.

The public registration process is designed to provide a straightforward onboarding experience while keeping administrative privileges restricted.

## 📧 2. Email OTP Verification

<!-- Screenshot: docs/screenshots/email-otp-verification.png -->

Email-based OTP verification is used to verify the email address supplied during registration.

The verification process integrates with the application's configured SMTP service.

**Verification Flow:**

1. The visitor enters an email address.
2. The application initiates an OTP verification request.
3. A six-digit verification code is sent through the configured email service.
4. The visitor submits the received code.
5. The backend verifies the submitted OTP.
6. After successful verification, the account can be created.

**Key Components:**
- Six-digit email verification codes.
- SMTP email integration.
- Backend verification services.
- Database-backed verification records.
- Registration verification migration.

## 🔑 3. User Authentication and Login

<!-- Screenshot: docs/screenshots/login.png -->

Registered users can access the application through the login interface.

The authentication system integrates with the backend account-management functionality to authenticate users and provide access to protected application resources.

**Key Capabilities:**
- User login.
- Account authentication.
- Protected application access.
- Operator and administrator role distinction.
- Integration with frontend authentication flows.

## 🛡️ 4. Role-Based Access Control

AgentOps-OS distinguishes between operator accounts and administrator accounts.

The role assignment mechanism is designed to prevent public registration from becoming a route to administrator privileges.

**Role Structure:**

| Role | Description |
|---|---|
| Operator | Default role assigned to accounts created through public registration |
| Administrator | Privileged account used for administrative operations |

**Important Security Rules:**
- Public registration assigns the `operator` role automatically.
- Visitors cannot choose the `admin` role during signup.
- Administrator account creation is handled separately.
- The legacy administrator invitation functionality remains optional.
- Protected application functionality uses authentication and authorization mechanisms.

## 🔄 5. Registration and Authentication Flow

The following diagram illustrates the public registration process.

```mermaid
flowchart TD
    A([Visitor])
    B[Registration Interface]
    C[Enter Email]
    D[Request OTP]
    E[Configured SMTP Service]
    F[Submit Six-Digit OTP]
    G[Backend OTP Verification]
    H{Verification Successful?}
    I[Create Operator Account]
    J[Automatic Sign-In]
    K[Application Dashboard]
    L[Verification Error]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H -->|Yes| I
    H -->|No| L
    I --> J
    J --> K
```

## 🔒 6. Administrator Account Management

Administrator accounts are managed separately from public self-service registration.

AgentOps-OS includes a backend management CLI for administrative user operations.

For example, an administrator account can be bootstrapped using:

```powershell
cd backend

uv run python scripts/manage_users.py bootstrap-admin --email your-email@example.com
```

To list existing accounts:

```powershell
uv run python scripts/manage_users.py list-users
```

This approach provides an administrative account-management mechanism without allowing visitors to assign themselves elevated privileges during registration.

## 🗄️ 7. Authentication Data Management

Authentication-related information is maintained through the application's database models and schema migrations.

The self-service registration verification functionality includes the migration:

```text
0008_public_registration_otp
```

The migration was successfully applied to the development PostgreSQL database, and Alembic confirmed that the database was at revision `0008 (head)`.

## 🧰 8. Security Engineering Practices

The platform incorporates several security-related application design practices.

**Implemented Security Areas:**
- Authentication and authorization mechanisms.
- Role-based account separation.
- Email verification during public registration.
- Protected backend application functionality.
- Authenticated, owner-scoped observability APIs.
- Environment-based configuration.
- Database-backed account management.
- Controlled administrator account creation.

**Configuration Recommendations:**
- Keep SMTP credentials in environment variables.
- Never commit private credentials to GitHub.
- Do not expose administrator credentials in source code.
- Use the provided environment example when configuring the application.
- Restrict access to privileged application operations.

## 🧪 9. Authentication Verification Status

The registration verification migration was successfully applied to the development database.

The following implementation areas are present:

| Capability | Implementation Status |
|---|---|
| Public registration | Implemented |
| Six-digit OTP verification | Implemented |
| SMTP integration | Implemented |
| Default operator role | Implemented |
| Public admin-role selection | Not permitted |
| Automatic sign-in after registration | Implemented |
| Administrator bootstrap CLI | Implemented |
| Optional administrator invitation | Retained for compatibility |

**End-to-End Verification Note:**

Database migration success confirms that the registration schema is applied. It does not, by itself, prove that the complete SMTP registration flow works.

The full registration journey—including receiving the email, verifying the OTP, creating an operator account, and automatically signing in—should be validated against the configured SMTP environment before being marked as end-to-end demonstrated.

## 💡 Engineering Value

The authentication and security implementation demonstrates practical experience with:

- User registration architecture.
- Email-based OTP verification.
- SMTP integration.
- Authentication and authorization.
- Role-based access control.
- Database migrations.
- Administrative account management.
- Protected backend APIs.
- Secure configuration practices.

**The objective is to provide controlled access to the AgentOps-OS platform while keeping public user onboarding separate from privileged administrative operations.**

---

# 🛠️ Technology Stack

AgentOps-OS is built using modern Python, frontend, database, and AI technologies to create a modular full-stack platform for managing AI-powered applications.

The technology stack combines backend API development, interactive frontend engineering, relational and vector data storage, LLM integrations, and automated software testing.

## 🎨 1. Frontend Technologies

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
</p>

The frontend provides the interactive application interface used to access workflow orchestration, knowledge management, agent capabilities, memory, analytics, and application settings.

| Technology | Purpose |
|---|---|
| React 19 | Component-based user interface development |
| TypeScript | Static typing and maintainable frontend code |
| Vite 8 | Frontend development server and production build |
| Tailwind CSS 4 | Utility-first interface styling |
| React Router 7 | Client-side navigation and routing |
| TanStack Query 5 | Server-state and API data management |
| Axios | HTTP communication with backend APIs |
| React Flow (`@xyflow/react`) | Visual workflow builder |
| Recharts | Analytics and chart visualization |
| Lucide React | Interface icons |
| Vitest | Frontend automated testing |

## ⚙️ 2. Backend Technologies

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API_Framework-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Pydantic-Data_Validation-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
</p>

The backend provides the API layer, application services, workflow execution functionality, AI integration, authentication, and persistent data management.

| Technology | Purpose |
|---|---|
| Python 3.12 | Primary backend programming language |
| FastAPI | REST API development |
| Pydantic 2 | Request validation and data schemas |
| SQLAlchemy 2 | Database ORM and persistence |
| Alembic | Version-controlled database migrations |
| Uvicorn | ASGI application server |
| Psycopg | PostgreSQL database connectivity |

## 🗄️ 3. Database Technologies

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/pgvector-Vector_Search-336791?style=for-the-badge" alt="pgvector">
  <img src="https://img.shields.io/badge/Alembic-Migrations-9B59B6?style=for-the-badge" alt="Alembic">
</p>

AgentOps-OS uses PostgreSQL as its primary persistent database and pgvector for vector-based knowledge retrieval.

| Technology | Purpose |
|---|---|
| PostgreSQL 16 | Relational application data storage |
| pgvector | Vector storage and similarity search |
| SQLAlchemy | Database interaction and ORM |
| Alembic | Database schema migrations |
| Psycopg | PostgreSQL connectivity |

The database layer supports application accounts, workflow records, task executions, knowledge data, memory records, approval information, and telemetry.

## 🤖 4. AI and LLM Technologies

<p align="center">
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
  <img src="https://img.shields.io/badge/OpenAI-Provider-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Groq-Provider-F55036?style=for-the-badge" alt="Groq">
</p>

The AI integration layer connects application capabilities with supported language-model and embedding providers.

| Technology | Purpose |
|---|---|
| Ollama | Locally hosted model integration |
| OpenAI | Supported hosted LLM provider |
| Groq | Supported hosted LLM provider |
| Qwen 3.5 0.8B | Local language model used during development |
| EmbeddingGemma | Local embedding model used during development |
| pgvector | Vector-based semantic retrieval |

**Local model configuration used during development:**

| Model | Purpose |
|---|---|
| `qwen3.5:0.8b` | Language-model integration |
| `embeddinggemma:latest` | Text embedding generation |

Local Ollama integration provides an option for running models without depending on a paid hosted inference API.

## 🧪 5. Testing and Code Quality

<p align="center">
  <img src="https://img.shields.io/badge/pytest-Backend_Testing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Vitest-Frontend_Testing-6E9F18?style=for-the-badge&logo=vitest&logoColor=white" alt="Vitest">
  <img src="https://img.shields.io/badge/Ruff-Linting_D%26Formatting-D7FF64?style=for-the-badge&logo=ruff&logoColor=black" alt="Ruff">
  <img src="https://img.shields.io/badge/mypy-Static_Typing-2A6DB2?style=for-the-badge" alt="mypy">
</p>

| Technology | Purpose |
|---|---|
| pytest | Backend unit and integration testing |
| Vitest | Frontend automated testing |
| Ruff | Python linting and formatting |
| mypy | Python static type checking |
| TypeScript | Frontend type checking |
| Vite Build | Frontend production-build verification |

## 🐳 6. Development and Infrastructure Tools

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Docker_Compose-Development-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/uv-Python_Packaging-DE5FE9?style=for-the-badge" alt="uv">
  <img src="https://img.shields.io/badge/Git-Version_Control-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
  <img src="https://img.shields.io/badge/GitHub-Source_Control-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</p>

| Technology | Purpose |
|---|---|
| Docker | Containerized infrastructure |
| Docker Compose | Local database infrastructure management |
| uv | Python dependency and environment management |
| npm | Frontend package management |
| Git | Version control |
| GitHub | Source-code hosting and project management |
| VS Code | Development environment |

## 🧩 7. Technology Stack Summary

| Category | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite 8, Tailwind CSS 4 |
| Frontend Libraries | React Router, TanStack Query, Axios, React Flow, Recharts, Lucide |
| Backend | Python 3.12, FastAPI, Pydantic 2, Uvicorn |
| Database | PostgreSQL 16, pgvector |
| ORM and Migrations | SQLAlchemy 2, Alembic, Psycopg |
| AI Providers | Ollama, OpenAI, Groq |
| Local Models | Qwen 3.5 0.8B, EmbeddingGemma |
| Backend Testing | pytest |
| Frontend Testing | Vitest |
| Code Quality | Ruff, mypy, TypeScript |
| Infrastructure | Docker, Docker Compose |
| Development Tools | uv, npm, Git, GitHub |

### 💡 Technology Selection Philosophy

The technology stack was selected to support:

- Modular backend architecture.
- Interactive full-stack application development.
- Persistent relational and vector data storage.
- Flexible AI provider integration.
- Local LLM experimentation.
- Maintainable code and automated testing.
- Reproducible local development.

**AgentOps-OS combines modern full-stack engineering with practical AI application infrastructure in one cohesive software project.**

---

# 🏗️ System Architecture

AgentOps-OS follows a modular full-stack architecture that integrates frontend interfaces, backend API services, AI orchestration components, knowledge retrieval, provider integrations, and persistent data storage.

The architecture separates presentation, API handling, application services, AI execution, and data persistence to make the platform easier to maintain and extend.

## 🧩 1. High-Level Architecture

The platform consists of the following major layers:

| Layer | Responsibility |
|---|---|
| Presentation Layer | React and TypeScript application interface |
| API Layer | FastAPI endpoints, request validation, authentication and authorization |
| Application Services | Workflow orchestration, tools, agents, approvals and knowledge operations |
| AI Integration Layer | Provider management, LLM execution and embedding integration |
| Persistence Layer | PostgreSQL, pgvector and application records |
| Operational Layer | Telemetry recording, analytics and execution visibility |

## 🖥️ 2. Presentation Layer

The presentation layer is responsible for user interaction and visualization.

**Technologies:**
- React 19.
- TypeScript.
- Vite.
- Tailwind CSS.
- React Router.
- TanStack Query.

**Responsibilities:**
- User authentication and application navigation.
- Workflow design and execution interfaces.
- Agent-related interactions.
- Knowledge document management.
- Memory management.
- Approval management.
- Provider configuration.
- Analytics and settings.

## ⚙️ 3. API and Backend Layer

The backend is built using Python and FastAPI.

It exposes versioned REST API endpoints under:

`/api/v1`

**Responsibilities:**
- Request handling.
- Request and response validation.
- Authentication and authorization.
- Application service coordination.
- Workflow and task management.
- Knowledge and memory operations.
- Provider configuration.
- Approval management.
- Observability APIs.

Pydantic schemas define validated data contracts, while SQLAlchemy provides database interaction.

## 🤖 4. AI and Application Service Layer

This layer coordinates the platform's AI-related and application-specific capabilities.

Major components include:

| Component | Responsibility |
|---|---|
| Workflow Planner | Organizes workflow definitions and tasks |
| Agent Orchestrator | Coordinates agent-related execution |
| Agent Registry | Organizes registered agent capabilities |
| Specialized Agents | Supports analysis and report-generation operations |
| Tool Registry | Provides registered backend tools |
| Task Execution | Executes configured workflow tasks |
| Knowledge Services | Handles document processing and retrieval |
| Memory Services | Manages persistent memory |
| Approval Services | Handles approval-related operations |
| Provider Manager | Coordinates supported AI provider integrations |
| Telemetry Services | Records operational events |

**Important workflow boundary:**

The visual workflow builder provides agent-oriented and tool-oriented task nodes, but the backend execution contract uses registered tools for task execution. It should not be interpreted as a separate autonomous multi-agent runtime for every visual agent node.

## 🧬 5. Knowledge and Retrieval Layer

The knowledge subsystem connects document processing with vector-based retrieval.

Its major components include:

- Document processing.
- Document chunking.
- Embedding generation.
- Vector storage.
- Semantic retrieval.
- Knowledge context integration.

PostgreSQL with pgvector provides the persistent vector-storage and retrieval foundation.

## 🔌 6. AI Provider Layer

The AI provider manager connects application services with supported model providers.

**Supported integrations:**
- Ollama.
- OpenAI.
- Groq.

The platform supports both local model execution through Ollama and configured hosted-provider integrations.

## 🗄️ 7. Persistence Layer

PostgreSQL provides persistent storage for application data.

The pgvector extension supports vector-based knowledge retrieval.

The persistence layer supports:

- User accounts and authentication data.
- Workflow and task records.
- Knowledge documents and vector representations.
- Agent memory records.
- Approval-related records.
- Telemetry and observability events.

## 📊 8. High-Level Architecture Diagram

```mermaid
flowchart TB

    USER([User / Administrator])

    subgraph FRONTEND["Presentation Layer"]
        UI["React 19 + TypeScript"]
        ROUTER["React Router"]
        QUERY["TanStack Query"]
        SCREENS["Dashboard, Workflows, Knowledge, Memory, Approvals, Settings"]
        
        UI --> ROUTER
        UI --> QUERY
        ROUTER --> SCREENS
    end

    subgraph BACKEND["Backend API Layer"]
        API["FastAPI - /api/v1"]
        AUTH["Authentication and Authorization"]
        SCHEMAS["Pydantic Validation"]
        ROUTES["API Routers"]
        
        API --> AUTH
        AUTH --> SCHEMAS
        SCHEMAS --> ROUTES
    end

    subgraph SERVICES["Application and AI Services"]
        WORKFLOW["Workflow Planner and Orchestration"]
        AGENTS["Specialized Agent Capabilities"]
        TOOLS["Tool Registry and Task Execution"]
        KNOWLEDGE["Knowledge Processing and Retrieval"]
        MEMORY["Persistent Memory Services"]
        APPROVALS["Human Approval Services"]
        PROVIDERS["AI Provider Manager"]
        TELEMETRY["Telemetry and Analytics"]
    end

    subgraph MODELS["AI Provider Layer"]
        OLLAMA["Ollama - Local Models"]
        OPENAI["OpenAI"]
        GROQ["Groq"]
        EMBEDDINGS["Embedding Model"]
    end

    subgraph STORAGE["Persistence Layer"]
        POSTGRES[("PostgreSQL")]
        PGVECTOR[("pgvector")]
        RECORDS["Application Records"]
        VECTORS["Document Embeddings"]
    end

    USER --> UI
    SCREENS --> API

    ROUTES --> WORKFLOW
    ROUTES --> AGENTS
    ROUTES --> TOOLS
    ROUTES --> KNOWLEDGE
    ROUTES --> MEMORY
    ROUTES --> APPROVALS
    ROUTES --> PROVIDERS
    ROUTES --> TELEMETRY

    WORKFLOW --> TOOLS
    WORKFLOW --> AGENTS
    AGENTS --> KNOWLEDGE
    AGENTS --> MEMORY
    AGENTS --> PROVIDERS
    KNOWLEDGE --> EMBEDDINGS

    PROVIDERS --> OLLAMA
    PROVIDERS --> OPENAI
    PROVIDERS --> GROQ
    EMBEDDINGS --> OLLAMA

    WORKFLOW --> POSTGRES
    TOOLS --> POSTGRES
    MEMORY --> POSTGRES
    APPROVALS --> POSTGRES
    TELEMETRY --> POSTGRES
    KNOWLEDGE --> POSTGRES
    KNOWLEDGE --> PGVECTOR

    POSTGRES --> RECORDS
    PGVECTOR --> VECTORS
```

*This diagram presents the platform's logical architecture. It groups related services for readability and does not represent every internal module or runtime call.*

## 🔄 9. Architectural Design Principles

AgentOps-OS follows several important software engineering principles.

**Modularity:**  
Application capabilities are organized into separate backend services and frontend modules.

**Separation of Responsibilities:**  
Presentation, API handling, business logic, AI integration, and data persistence have distinct responsibilities.

**Provider Abstraction:**  
AI provider integrations are organized separately from application-level AI functionality.

**Persistent Data Management:**  
Application operations and AI-related records are maintained using PostgreSQL.

**Extensibility:**  
The architecture provides a foundation for adding tools, providers, and application capabilities.

**Observability:**  
Structured telemetry and analytics APIs provide visibility into operational activity.

### 💡 Architecture Goal

The architectural objective is to create a maintainable full-stack platform in which AI capabilities, workflow execution, knowledge retrieval, and operational management can coexist within a consistent application architecture.

---

# 🔄 Application Request Flow

AgentOps-OS uses a frontend-to-backend request architecture in which the React application communicates with versioned FastAPI REST endpoints.

The backend authenticates requests, validates incoming data, delegates operations to application services, interacts with AI providers or tools when required, and returns structured responses to the frontend.

## 🌐 1. Standard API Request Flow

When a user performs an application operation, the following sequence generally takes place:

1. The user interacts with a React interface.
2. The frontend initiates an API request.
3. The request is sent to the FastAPI backend.
4. Authentication and authorization checks are applied where required.
5. The API endpoint validates the request.
6. The appropriate application service processes the operation.
7. The service interacts with the database or other required components.
8. The backend returns a structured response.
9. The frontend updates the interface with the returned information.

## 🧭 2. Request Lifecycle Diagram

```mermaid
sequenceDiagram
    autonumber

    actor User
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant Auth as Authentication
    participant Service as Application Services
    participant DB as PostgreSQL

    User->>UI: Perform application action
    UI->>API: HTTP request to /api/v1
    API->>Auth: Validate identity and permissions
    Auth-->>API: Authorization result

    API->>Service: Validated application request
    Service->>DB: Read or write application data
    DB-->>Service: Database result

    Service-->>API: Operation result
    API-->>UI: JSON response
    UI-->>User: Updated application interface
```

## 🔄 3. Workflow Execution Request

Workflow execution involves additional application services responsible for managing tasks, dependencies, and registered tools.

**Execution Sequence:**

1. A user creates a workflow through the visual builder.
2. The frontend prepares a workflow definition.
3. The workflow definition is submitted to the backend.
4. The backend validates the workflow and task information.
5. The backend creates the associated workflow run and task records.
6. The execution service evaluates task dependencies.
7. Eligible tasks are executed using registered backend tools.
8. Execution results and task states are persisted.
9. Workflow information becomes available through the application APIs.
10. The frontend displays the available execution information.

### Workflow Execution Sequence

```mermaid
sequenceDiagram
    autonumber

    actor User
    participant UI as Workflow Builder
    participant API as FastAPI
    participant Workflow as Workflow Services
    participant Executor as Task Executor
    participant Tools as Tool Registry
    participant DB as PostgreSQL

    User->>UI: Configure workflow
    UI->>API: Submit workflow definition
    API->>Workflow: Validate and create run
    Workflow->>DB: Persist workflow and task records
    DB-->>Workflow: Created run

    Workflow->>Executor: Execute workflow
    Executor->>Executor: Evaluate task dependencies
    Executor->>Tools: Invoke registered tool
    Tools-->>Executor: Tool result

    Executor->>DB: Persist task state and result
    DB-->>Executor: Persistence confirmation

    Executor-->>Workflow: Execution result
    Workflow-->>API: Run information
    API-->>UI: Structured response
    UI-->>User: Display execution information
```

## 🤖 4. AI Agent and LLM Request Flow

AI-related application operations may require interaction with a configured LLM provider.

The provider-management layer separates application-level functionality from provider-specific communication.

**Execution Sequence:**

1. An AI-related request originates from an application interface or supported backend operation.
2. The backend routes the request to the relevant application or agent service.
3. The service prepares the required input and context.
4. Relevant knowledge may be retrieved when the operation uses RAG.
5. The provider manager selects the configured provider.
6. The provider receives the model request.
7. The model generates a response.
8. The backend processes the result.
9. The application returns the result to the requesting interface.

### AI Provider Request Diagram

```mermaid
sequenceDiagram
    autonumber

    actor User
    participant UI as React Frontend
    participant API as FastAPI
    participant Agent as Agent / Application Service
    participant Provider as Provider Manager
    participant Model as Configured LLM

    User->>UI: Submit AI request
    UI->>API: Send authenticated request
    API->>Agent: Process application operation
    Agent->>Provider: Request model generation
    Provider->>Model: Submit model input
    Model-->>Provider: Generated response
    Provider-->>Agent: Provider result
    Agent-->>API: Processed application result
    API-->>UI: JSON response
    UI-->>User: Display result
```

## 📚 5. Knowledge Retrieval Request Flow

Knowledge-based requests use the RAG subsystem to retrieve relevant information from indexed documents.

**Retrieval Sequence:**

1. A user submits a knowledge-related query.
2. The backend receives and validates the request.
3. The knowledge service prepares the query for retrieval.
4. The embedding functionality generates a query vector where required.
5. pgvector performs semantic similarity retrieval.
6. Relevant knowledge information is returned.
7. Retrieved context is supplied to the supported AI operation.
8. The configured LLM provider generates a response.
9. The application returns the result and available source information.

### Knowledge Retrieval Diagram

```mermaid
sequenceDiagram
    autonumber

    actor User
    participant UI as Knowledge Interface
    participant API as FastAPI
    participant RAG as Knowledge Services
    participant Vector as PostgreSQL + pgvector
    participant Model as AI Provider

    User->>UI: Submit knowledge query
    UI->>API: Send query
    API->>RAG: Process retrieval request
    RAG->>Vector: Perform semantic retrieval
    Vector-->>RAG: Relevant document information
    RAG->>Model: Submit query with retrieved context
    Model-->>RAG: Generated response
    RAG-->>API: Response and available source information
    API-->>UI: Structured result
    UI-->>User: Display answer
```

## 🗄️ 6. Database Interaction

PostgreSQL acts as the primary persistent storage layer.

Different application services interact with the database depending on the operation being performed.

| Application Component | Database Responsibility |
|---|---|
| Authentication | User and verification records |
| Workflow Services | Workflow and execution records |
| Task Executor | Task states and execution results |
| Knowledge Services | Document and retrieval-related data |
| Agent Memory | Persistent memory records |
| Approval Services | Approval-related records |
| Telemetry Services | Operational event records |

The pgvector extension supports vector-based semantic retrieval for the knowledge subsystem.

## 📡 7. API Communication

AgentOps-OS exposes versioned backend REST endpoints under:

```text
/api/v1
```

During local frontend development, the Vite development server forwards `/api/*` requests to the backend at:

```text
http://127.0.0.1:8000
```

This allows the frontend to communicate with the backend through a development proxy.

The backend API documentation is available through FastAPI's Swagger interface:

```text
http://127.0.0.1:8000/docs
```

## 🧩 8. Error Handling and Operational Visibility

Application requests may involve database operations, tool execution, workflow processing, or external model integrations.

AgentOps-OS uses backend application services, execution records, and telemetry to support operational inspection.

**Important areas include:**
- API request validation.
- Authentication and authorization failures.
- Workflow and task execution states.
- Tool execution results.
- Provider-related outcomes.
- Persistent execution records.
- Structured telemetry events.

## 💡 Request Architecture Summary

The general request lifecycle can be summarized as:

**User → React Frontend → FastAPI → Application Services → Tools / Agents / Providers / Database → API Response → Frontend**

Not every request uses an AI agent or external model. Ordinary operations such as authentication, document listing, memory management, and analytics retrieval can be handled directly by their respective backend services.

This separation helps keep the platform modular and avoids unnecessary AI-provider calls for operations that do not require them.

---

# 🧬 RAG Architecture

AgentOps-OS implements a Retrieval-Augmented Generation (RAG) pipeline that connects uploaded knowledge documents with specialized AI capabilities.

The RAG architecture combines document processing, text chunking, embedding generation, vector storage, semantic retrieval, optional memory recall, and LLM-powered response generation.

Its purpose is to provide AI operations with relevant, application-specific information retrieved from indexed knowledge sources.

## 📄 1. Supported Document Types

The knowledge ingestion pipeline supports the following document formats:

| File Format | Media Type | Processing |
|---|---|---|
| PDF | `application/pdf` | Page-based text extraction using pypdf |
| TXT | `text/plain` | UTF-8 text extraction |
| Markdown | `text/markdown` | UTF-8 text extraction |

The processing layer also performs filename validation, input validation, and document safety checks before preparing content for indexing.

## ⚙️ 2. Document Ingestion and Processing

<!-- Screenshot: docs/screenshots/knowledge-base.png -->

When a user uploads a document, the backend processes the file before storing its searchable representation.

**Processing Steps:**

1. Receive the uploaded document.
2. Validate the filename and supported file type.
3. Validate the document content.
4. Extract text from the document.
5. Preserve page information where applicable.
6. Normalize the extracted text.
7. Divide the content into searchable chunks.
8. Generate embeddings for the chunks.
9. Store document and chunk information in PostgreSQL.

The processing implementation uses `pypdf` for PDF extraction and UTF-8 decoding for TXT and Markdown files.

## ✂️ 3. Document Chunking

Large documents are divided into smaller text segments before embedding generation.

Each chunk maintains source-location information so that retrieved content can be associated with its original document.

**Chunk Information:**

- Document identifier.
- Chunk index.
- Extracted content.
- PDF page number, when available.
- Starting character position.
- Ending character position.
- Chunk metadata.
- Vector embedding.

**Default Configuration:**

| Setting | Default |
|---|---:|
| Chunk size | 1,200 characters |
| Chunk overlap | 200 characters |
| Maximum upload size | 10 MB |
| Maximum PDF pages | 200 |
| Maximum chunks per document | 5,000 |

These values are configurable through the backend application settings.

## 🧠 4. Embedding Generation

After document chunking, the embedding service converts textual chunks into numerical vector representations.

AgentOps-OS integrates a local Ollama embedding client for embedding generation.

**Development Configuration:**

| Component | Value |
|---|---|
| Embedding Runtime | Ollama |
| Embedding Model | `embeddinggemma:latest` |
| Vector Dimensions | 768 |
| Embedding Endpoint | Ollama `/api/embed` |

The embedding service validates the vector dimensions and processes text in batches.

The database schema expects 768-dimensional vectors, so the configured embedding model must produce compatible embeddings.

## 🗄️ 5. Vector Storage with PostgreSQL and pgvector

The generated embeddings are stored alongside their corresponding knowledge chunks.

The database uses two primary knowledge entities:

| Entity | Responsibility |
|---|---|
| `KnowledgeDocument` | Stores uploaded document metadata |
| `KnowledgeChunk` | Stores searchable text chunks and embeddings |

The `knowledge_documents` table maintains document ownership and metadata.

The `knowledge_chunks` table stores the extracted content, source-location information, and vector representations.

AgentOps-OS also defines an HNSW vector index using cosine similarity operations for knowledge retrieval.

## 🔍 6. Semantic Search and Retrieval

<!-- Screenshot: docs/screenshots/knowledge-search.png -->

When a user submits a knowledge query, the retrieval service searches the indexed knowledge associated with the authenticated user.

**Retrieval Process:**

1. Receive the user's query.
2. Resolve the authenticated user's ownership context.
3. Generate a query embedding.
4. Search eligible indexed document chunks.
5. Rank relevant passages using vector similarity.
6. Return the selected knowledge passages.
7. Preserve document and source-location information.

The retrieval response includes information such as:

- Source identifier.
- Filename.
- Document identifier.
- Page number, where available.
- Chunk index.
- Similarity score.
- Retrieved content.

The RAG service also supports restricting retrieval to selected document identifiers.

If no relevant passages are found, the service returns a `NoRelevantKnowledgeError` rather than silently generating an unsupported knowledge answer.

## 🤖 7. Knowledge-Grounded Agent Execution

After retrieval, the RAG service prepares an agent context containing the retrieved passages.

The selected agent receives:

- The user's question.
- The authenticated actor's role.
- Retrieved document evidence.
- Source identifiers.
- Available recalled memories, when configured.
- Execution metadata.

The agent is instructed to treat retrieved passages as reference data, use relevant evidence for factual claims, and identify insufficient evidence where appropriate.

The generated result is returned together with the retrieved source information.

This allows the application to associate an AI-generated answer with the knowledge passages supplied during execution.

## 🧠 8. Optional Memory Integration

The RAG service can also integrate persistent agent memory.

When memory retrieval is configured, the service searches for relevant memories using the authenticated user's ownership context and selected agent identity.

Retrieved memories are treated as untrusted reference information. They must not override system instructions, current user requests, or authorization rules.

Automatic capture of successful RAG interactions is configurable and disabled by default.

## 🔄 9. Complete RAG Pipeline

```mermaid
flowchart TD
    A([Document Upload])
    B[Filename and File Validation]
    C[PDF / TXT / Markdown Extraction]
    D[Text Normalization]
    E[Deterministic Chunking]
    F[Ollama Embedding Service]
    G[768-Dimensional Vectors]
    H[(PostgreSQL + pgvector)]

    I([User Knowledge Query])
    J[Query Embedding]
    K[Owner-Scoped Semantic Search]
    L[Relevant Document Chunks]
    M[Source Metadata and Citations]
    N[Optional Memory Retrieval]
    O[Agent Context Construction]
    P[Registered Specialized Agent]
    Q[Configured LLM Provider]
    R([Grounded Response])

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H

    I --> J
    J --> K
    H --> K
    K --> L
    L --> M
    M --> O
    N --> O
    O --> P
    P --> Q
    Q --> R
```

## 🧪 10. Demonstrated RAG Workflow

The knowledge pipeline was exercised during application validation.

The demonstrated workflow included:

1. Uploading a TXT document.
2. Processing and indexing the document.
3. Searching indexed knowledge.
4. Retrieving relevant content and citation information.
5. Sending a knowledge-related request to the Analysis Agent.
6. Generating a knowledge-supported report through the Report Agent.

The knowledge upload, indexing, search, and agent interactions were demonstrated through the running frontend.

## 🏗️ 11. Relevant Implementation Files

| File | Responsibility |
|---|---|
| `services/document_processing.py` | Document extraction and chunking |
| `services/embeddings.py` | Ollama embedding integration |
| `services/knowledge_base.py` | Knowledge persistence and retrieval |
| `services/rag.py` | RAG context construction and agent execution |
| `db/models/knowledge.py` | Knowledge document and chunk models |
| `api/v1/knowledge.py` | Knowledge management APIs |
| `schemas/knowledge.py` | Knowledge request and response schemas |

## 💡 Engineering Value

The RAG implementation demonstrates practical experience with:

- Document ingestion and processing.
- PDF text extraction.
- Deterministic text chunking.
- Embedding generation.
- Local embedding-model integration.
- Vector database architecture.
- HNSW vector indexing.
- Cosine similarity retrieval.
- Owner-scoped knowledge access.
- Source-grounded AI responses.
- Persistent memory integration.

**The objective is to make AI application responses more context-aware by connecting model execution with searchable, application-specific knowledge.**

---

# 🔄 Agent Execution Lifecycle

AgentOps-OS provides structured execution mechanisms for managing workflow tasks and specialized AI agent operations.

The execution architecture includes planning, validation, dependency management, tool execution, agent orchestration, persistent state, error handling, and operational telemetry.

## 🧩 1. Execution Components

| Component | Responsibility |
|---|---|
| Workflow Planner | Converts a goal into a validated workflow definition |
| Agent Registry | Registers agents and their execution contracts |
| Agent Orchestrator | Coordinates registered agents using dependency-aware plans |
| Tool Registry | Registers tools with input and output contracts |
| Execution Service | Creates and executes workflow tasks |
| Task Runner | Executes registered handlers in an isolated child process |
| Memory Service | Retrieves and manages persistent agent memory |
| RAG Service | Supplies retrieved knowledge and memory context to agents |
| Provider Manager | Integrates supported LLM providers |
| Telemetry Recorder | Records provider and agent execution information |

## 📝 2. Planning and Validation

A workflow may begin with a user-defined goal or a structured workflow definition.

The workflow planning service can use an LLM to generate a structured workflow plan.

Before the plan is accepted, it is validated against application rules.

**Validation includes:**
- Non-empty workflow goals.
- Valid actor roles.
- Registered tool names.
- Unique task identifiers.
- Tool input-schema compatibility.
- Valid dependency references.
- Circular-dependency prevention.
- Restricted tool access.

The planner is responsible for generating and validating workflow plans. It does not execute the workflow itself.

## 🗄️ 3. Workflow Persistence

After successful validation, the execution service creates persistent workflow records.

The primary entities are:

- `WorkflowRun`
- `TaskRun`
- `TaskDependency`
- `ExecutionEvent`

The database stores task inputs, execution states, outputs, errors, and dependency relationships.

This provides a persistent representation of the workflow execution lifecycle.

## 🔗 4. Dependency-Aware Execution

Before executing tasks, the workflow execution service evaluates their dependency graph.

Tasks are organized using prerequisite-first topological ordering.

**Execution Rules:**
- Tasks with no prerequisites are eligible to execute first.
- A dependent task executes only after all its prerequisites succeed.
- Tasks blocked by unsuccessful prerequisites are skipped.
- Circular and invalid dependency references are rejected.
- Previously successful tasks are not repeated when an approval-paused workflow resumes.

This mechanism provides structured execution control for multi-step workflows.

## 🛠️ 5. Registered Tool Execution

Workflow tasks are executed through registered tool handlers.

Before execution, the platform performs checks against the registered tool definition.

**Execution Controls:**
- Tool registration.
- Role-based tool authorization.
- Input-schema validation.
- Output-schema validation.
- Configurable retry attempts.
- Per-task execution timeout.
- Structured error handling.
- Persistent execution results.

The task runner executes handlers in a separate child process and applies a hard execution timeout.

This creates an isolated execution boundary for registered task handlers.

## 🧑‍⚖️ 6. Human Approval Checkpoint

Some registered tools require approval before execution.

The approval requirement comes from the trusted tool definition rather than untrusted task input or LLM-generated workflow content.

When a task requires approval:

1. The execution service identifies the approval requirement.
2. An approval request is created if one does not already exist.
3. The task enters the `awaiting_approval` state.
4. The workflow enters the `awaiting_approval` state.
5. Execution returns control without running the protected task.
6. An authorized human can review and decide the request.
7. The workflow can resume after approval.
8. Previously successful tasks are not executed again.

## 🔄 7. Workflow Execution Lifecycle Diagram

```mermaid
flowchart TD
    A([User Workflow Request])
    B[Workflow Planner]
    C[Plan Validation]
    D{Plan Valid?}
    E[Persist WorkflowRun and TaskRun]
    F[Persist Task Dependencies]
    G[Dependency Ordering]
    H[Check Prerequisites]
    I{Prerequisites Succeeded?}
    J[Mark Task Skipped]
    K[Resolve Registered Tool]
    L[Check Role Authorization]
    M{Approval Required?}
    N[Create Approval Request]
    O[Pause Workflow]
    P[Human Review]
    Q{Approved?}
    R[Execute Registered Tool]
    S[Validate Input and Output]
    T[Child Process with Timeout]
    U[Persist Task Result and Event]
    V{All Tasks Complete?}
    W([Workflow Succeeded])
    X([Workflow Failed])

    A --> B
    B --> C
    C --> D
    D -->|No| X
    D -->|Yes| E
    E --> F
    F --> G
    G --> H
    H --> I

    I -->|No| J
    I -->|Yes| K

    J --> V
    K --> L
    L --> M

    M -->|Yes| N
    N --> O
    O --> P
    P --> Q
    Q -->|No| X
    Q -->|Yes| R

    M -->|No| R
    R --> S
    S --> T
    T --> U
    U --> V

    V -->|More Tasks| H
    V -->|Complete| W
```

*The diagram illustrates the logical lifecycle. An approval-paused workflow is resumed through a subsequent execution request after the required decision has been recorded.*

## 🤖 8. Specialized Agent Orchestration

Alongside workflow tool execution, AgentOps-OS implements a specialized-agent orchestration service.

The `AgentRegistry` maintains registered agent definitions, permitted roles, tool permissions, and output contracts.

The `AgentOrchestrator` coordinates agent tasks according to their dependency relationships.

**Key Capabilities:**
- Registered agent definitions.
- Role-based agent authorization.
- Dependency-aware agent execution.
- Validated agent output contracts.
- Explicitly retryable execution failures.
- Total execution-attempt budgets.
- Cumulative context-size budgets.
- Optional persistent memory retrieval.
- Optional agent-state persistence.

## 🧠 9. Agent Context and Memory

The agent orchestrator can retrieve relevant memories before executing an agent task.

When memory support is enabled:

1. The authenticated user identity is supplied by trusted application code.
2. The memory service searches eligible memories.
3. Relevant memories are added to the agent context.
4. The agent processes the task with the additional context.
5. The orchestration service records the task outcome.
6. Optional state persistence maintains the execution result.

Memory retrieval is owner-scoped, and memory content is treated as untrusted reference information.

## 🔄 10. Specialized Agent Orchestration Diagram

```mermaid
flowchart TD
    A([Orchestration Request])
    B[Orchestration Plan]
    C[Validate Agent Registration]
    D[Authorize Requested Agents]
    E[Build Dependency Order]
    F[Create Execution Budget]
    G[Check Task Dependencies]
    H[Collect Prior Successful Results]
    I[Retrieve Optional Agent Memory]
    J[Build AgentContext]
    K[AgentRegistry]
    L[Execute Registered Agent]
    M[Validate AgentResult]
    N[Record Task Outcome]
    O[Optional State Persistence]
    P{More Agent Tasks?}
    Q([Orchestration Result])

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    P -->|Yes| G
    P -->|No| Q
```

## 🛡️ 11. Execution Safety and Failure Handling

AgentOps-OS includes several execution safeguards.

| Safeguard | Purpose |
|---|---|
| Role Authorization | Restricts agent and tool access |
| Input Validation | Validates task inputs against declared schemas |
| Output Validation | Checks handler and agent output contracts |
| Dependency Validation | Rejects invalid or circular task dependencies |
| Retry Limits | Bounds configured execution attempts |
| Execution Timeout | Limits registered task-handler runtime |
| Attempt Budget | Bounds cumulative agent execution attempts |
| Context Budget | Limits cumulative serialized agent context size |
| Human Approval | Introduces review checkpoints for protected tools |
| Persistent Events | Maintains workflow execution information |

## 📊 12. Execution Monitoring

Workflow and task execution information is persisted and exposed through the platform's APIs.

The application can use this information to present:
- Workflow status.
- Individual task status.
- Execution output.
- Error information.
- Approval state.
- Execution events.
- Relevant telemetry.

## 🏗️ 13. Relevant Implementation Files

| File | Responsibility |
|---|---|
| `services/planner.py` | LLM-backed workflow planning and validation |
| `services/orchestrator.py` | Specialized-agent orchestration |
| `services/agent_registry.py` | Agent registration and execution contracts |
| `services/execution.py` | Workflow and task execution |
| `services/task_runner.py` | Isolated task-handler execution |
| `services/tool_registry.py` | Tool definitions, authorization and contracts |
| `services/agent_state.py` | Agent execution-state persistence |
| `services/agent_memory.py` | Persistent memory operations |
| `services/rag.py` | Knowledge-grounded agent execution |

### 💡 Engineering Value

The execution architecture demonstrates practical experience with:

- AI workflow planning.
- Dependency graph validation.
- Topological task ordering.
- Tool registration and contracts.
- Role-based execution controls.
- Isolated task execution.
- Retry and timeout management.
- Specialized-agent orchestration.
- Context and execution budgets.
- Persistent state and memory.
- Human approval checkpoints.

**The objective is to make AI execution structured, controlled, inspectable, and maintainable rather than treating every model interaction as an isolated request.**

---

# 🗄️ Database Design

AgentOps-OS uses PostgreSQL as its primary relational database and pgvector for vector-based knowledge retrieval and persistent memory search.

The data layer is implemented using SQLAlchemy 2 and managed through version-controlled Alembic migrations.

The database design organizes application identity, workflow execution, knowledge management, memory, approvals, provider configuration, and observability into separate but related entities.

## 🧩 1. Database Technology

| Technology | Responsibility |
|---|---|
| PostgreSQL 16 | Primary relational database |
| pgvector | Vector storage and similarity search |
| SQLAlchemy 2 | ORM and database interaction |
| Psycopg 3 | PostgreSQL driver |
| Alembic | Version-controlled schema migrations |

## 👥 2. Identity and Authentication Entities

### `users`

Stores application user identity and role information.

**Important responsibilities:**
- User email.
- Password hash.
- Account role.
- Active-account status.
- Creation and update timestamps.

### `auth_action_tokens`

Stores single-use authentication action tokens for supported account flows.

**Supported purposes:**
- Registration.
- Administrator invitation.
- Password recovery.

The database stores a keyed token digest rather than the raw OTP value.

### `audit_logs`

Maintains security-relevant application audit records.

The implementation uses database triggers to prevent ordinary UPDATE, DELETE, and TRUNCATE operations on the audit table.

## 🔄 3. Workflow Execution Entities

### `workflow_runs`

Represents an individual execution of a workflow goal.

**Important information:**
- Workflow creator.
- Goal.
- Workflow status.
- Execution plan.
- Error information.
- Start and completion timestamps.

### `task_runs`

Represents an individual task within a workflow.

**Important information:**
- Parent workflow.
- Task key and name.
- Registered tool name.
- Input and output data.
- Execution status.
- Attempt count.
- Maximum attempts.
- Execution timeout.
- Start and completion timestamps.

### `task_dependencies`

Maintains dependency relationships between tasks within the same workflow.

The database uses composite foreign keys to ensure that a dependency cannot connect tasks belonging to different workflows.

### `execution_events`

Stores append-only workflow and task execution events.

These records provide operational information about workflow activity.

## 📚 4. Knowledge Management Entities

### `knowledge_documents`

Stores uploaded document metadata and ownership information.

**Important information:**
- Document owner.
- Filename.
- Media type.
- SHA-256 document hash.
- Page count.
- Chunk count.
- Creation and update timestamps.

### `knowledge_chunks`

Stores the searchable content extracted from uploaded documents.

**Important information:**
- Parent document.
- Chunk index.
- Page number.
- Character positions.
- Extracted text.
- Vector embedding.
- Chunk metadata.

The embedding column uses a 768-dimensional pgvector representation.

## 🧠 5. Persistent Memory Entity

### `agent_memories`

Stores persistent episodic and semantic memory records.

**Important information:**
- Memory owner.
- Memory type.
- Memory scope.
- Optional agent key.
- Memory content.
- Vector embedding.
- Embedding model.
- Confidence score.
- Importance score.
- Source type.
- Optional source workflow.
- Metadata.
- Expiration and access information.

The table uses a vector index to support similarity-based memory retrieval.

## 🧑‍⚖️ 6. Approval Entity

### `approval_requests`

Stores approval requests associated with protected workflow tasks.

**Important information:**
- Parent workflow.
- Associated task.
- Requesting user.
- User recording the decision.
- Tool name.
- Action summary.
- Input snapshot.
- Approval status.
- Decision reason.
- Request and expiration timestamps.
- Decision timestamp.

An approval request is associated with a specific task and workflow.

## 🔌 7. AI Provider Configuration Entity

### `ai_provider_configs`

Stores per-user AI provider configuration information.

**Important information:**
- Provider owner.
- Provider identifier.
- Model name.
- Encrypted API credential.
- Provider base URL.
- Priority.
- Enabled status.
- Provider metadata.

The database supports the provider identifiers:
- `openai`
- `groq`
- `ollama`

Hosted-provider credentials are stored as encrypted values rather than being stored as ordinary plaintext API keys.

## 📊 8. Observability Entity

### `telemetry_events`

Stores structured telemetry associated with provider and agent execution attempts.

**Important information:**
- Event owner.
- Optional workflow identifier.
- Request identifier.
- Event type.
- Component attribution.
- Optional agent name.
- Provider identifier.
- Model identifier.
- Execution outcome.
- Duration.
- Optional token fields.
- Error type.
- Structured attributes.

The observability implementation intentionally avoids storing prompts, model outputs, provider response bodies, and API keys in telemetry records.

## 🔗 9. Database Entity Relationship Diagram

The following diagram shows the main application entities and their relationships.

```mermaid
erDiagram

    USERS ||--o{ WORKFLOW_RUNS : creates
    WORKFLOW_RUNS ||--|{ TASK_RUNS : contains

    WORKFLOW_RUNS ||--o{ EXECUTION_EVENTS : records
    TASK_RUNS ||--o{ EXECUTION_EVENTS : produces

    TASK_RUNS ||--o{ TASK_DEPENDENCIES : prerequisite_of
    TASK_RUNS ||--o{ TASK_DEPENDENCIES : depends_on

    USERS ||--o{ KNOWLEDGE_DOCUMENTS : owns
    KNOWLEDGE_DOCUMENTS ||--|{ KNOWLEDGE_CHUNKS : contains

    USERS ||--o{ AGENT_MEMORIES : owns
    WORKFLOW_RUNS ||--o{ AGENT_MEMORIES : may_source

    WORKFLOW_RUNS ||--o{ APPROVAL_REQUESTS : includes
    TASK_RUNS ||--o| APPROVAL_REQUESTS : may_require
    USERS ||--o{ APPROVAL_REQUESTS : requests
    USERS ||--o{ APPROVAL_REQUESTS : decides

    USERS ||--o{ AI_PROVIDER_CONFIGS : configures

    USERS ||--o{ TELEMETRY_EVENTS : owns
    WORKFLOW_RUNS ||--o{ TELEMETRY_EVENTS : attributes

    USERS ||--o{ AUTH_ACTION_TOKENS : creates
    USERS ||--o{ AUDIT_LOGS : performs

    USERS {
        uuid id PK
        string email
        string password_hash
        string role
        boolean is_active
    }

    WORKFLOW_RUNS {
        uuid id PK
        uuid created_by FK
        string goal
        string status
        json plan
        json error
    }

    TASK_RUNS {
        uuid id PK
        uuid workflow_run_id FK
        string key
        string name
        string tool_name
        string status
        json input_data
        json output_data
    }

    TASK_DEPENDENCIES {
        uuid task_id PK
        uuid depends_on_task_id PK
        uuid workflow_run_id FK
    }

    EXECUTION_EVENTS {
        bigint id PK
        uuid workflow_run_id FK
        uuid task_run_id FK
        string event_type
        string level
    }

    KNOWLEDGE_DOCUMENTS {
        uuid id PK
        uuid owner_id FK
        string filename
        string media_type
        string sha256
        integer chunk_count
    }

    KNOWLEDGE_CHUNKS {
        uuid id PK
        uuid document_id FK
        integer chunk_index
        text content
        vector embedding
    }

    AGENT_MEMORIES {
        uuid id PK
        uuid owner_user_id FK
        uuid source_workflow_run_id FK
        string memory_type
        string memory_scope
        text content
        vector embedding
    }

    APPROVAL_REQUESTS {
        uuid id PK
        uuid workflow_run_id FK
        uuid task_run_id FK
        uuid requester_user_id FK
        uuid decided_by_user_id FK
        string status
    }

    AI_PROVIDER_CONFIGS {
        uuid id PK
        uuid owner_user_id FK
        string provider
        string model_name
        text api_key_ciphertext
        boolean enabled
    }

    TELEMETRY_EVENTS {
        uuid id PK
        uuid owner_user_id FK
        uuid workflow_run_id FK
        string provider
        string model
        string outcome
        float duration_ms
    }
```

*This is a logical overview of the principal database entities. Some relationships are optional, and some tables such as authentication tokens and audit records are omitted from the diagram's detailed column representation for readability.*

## 🔄 10. Database Migration History

AgentOps-OS uses Alembic to manage schema changes through versioned migration files.

| Migration | Description |
|---|---|
| `0001_initial_schema` | Initial application schema |
| `0002_knowledge_base` | Knowledge document and vector storage |
| `0003_ai_providers_and_approvals` | AI provider configuration and approval records |
| `0004_persistent_agent_memory` | Persistent agent memory |
| `0005_observability_telemetry` | Telemetry and observability records |
| `0006_auth_action_tokens` | Authentication action tokens |
| `0007_email_otp_security` | Email OTP security improvements |
| `0008_public_registration_otp` | Public self-service registration verification |

The development database was successfully migrated to revision `0008 (head)` during project validation.

## 🔐 11. Data Integrity and Ownership

The database design includes several integrity mechanisms.

**Ownership:**
- User-owned knowledge documents.
- User-scoped memory records.
- User-owned provider configurations.
- Owner-scoped telemetry information.

**Referential Integrity:**
- Foreign-key constraints.
- Composite workflow/task relationships.
- Unique constraints.
- Check constraints.
- Cascading behavior where explicitly configured.

**Vector Storage:**
- 768-dimensional embeddings.
- HNSW vector indexes.
- Cosine similarity operations.

**Auditability:**
- Persistent execution events.
- Security-related audit records.
- Append-only audit protection through database triggers.

## 💡 Engineering Value

The database architecture demonstrates practical experience with:

- Relational database design.
- SQLAlchemy ORM.
- PostgreSQL constraints and indexes.
- Composite foreign keys.
- Database normalization.
- Vector data storage.
- HNSW indexing.
- Schema migration management.
- Persistent workflow execution.
- Owner-scoped data access.
- Audit and telemetry persistence.

**The objective is to maintain a consistent data foundation for application identity, AI execution, knowledge retrieval, persistent memory, approvals, and operational observability.**

---

# 📁 Repository Structure

AgentOps-OS follows a modular repository structure that separates the Python backend, React frontend, database migrations, infrastructure configuration, and automated tests.

The backend uses a service-oriented organization, while the frontend groups components and services by application feature.

## 🗂️ Project Directory Overview

```text
AgentOps-OS/
│
├── backend/
│   │
│   ├── migrations/
│   │   ├── versions/
│   │   │   ├── 0001_initial_schema.py
│   │   │   ├── 0002_knowledge_base.py
│   │   │   ├── 0003_ai_providers_and_approvals.py
│   │   │   ├── 0004_persistent_agent_memory.py
│   │   │   ├── 0005_observability_telemetry.py
│   │   │   ├── 0006_auth_action_tokens.py
│   │   │   ├── 0007_email_otp_security.py
│   │   │   └── 0008_public_registration_otp.py
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── scripts/
│   │   └── manage_users.py
│   │
│   ├── src/
│   │   └── agentops/
│   │       │
│   │       ├── api/
│   │       │   ├── v1/
│   │       │   │   ├── ai_providers.py
│   │       │   │   ├── approvals.py
│   │       │   │   ├── auth.py
│   │       │   │   ├── health.py
│   │       │   │   ├── knowledge.py
│   │       │   │   ├── memories.py
│   │       │   │   ├── observability.py
│   │       │   │   ├── router.py
│   │       │   │   └── runs.py
│   │       │   └── deps.py
│   │       │
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   ├── context.py
│   │       │   ├── encryption.py
│   │       │   ├── logging.py
│   │       │   ├── middleware.py
│   │       │   ├── observability_context.py
│   │       │   └── security.py
│   │       │
│   │       ├── db/
│   │       │   ├── models/
│   │       │   │   ├── ai_provider.py
│   │       │   │   ├── approval.py
│   │       │   │   ├── audit.py
│   │       │   │   ├── auth_action_token.py
│   │       │   │   ├── enums.py
│   │       │   │   ├── knowledge.py
│   │       │   │   ├── memory.py
│   │       │   │   ├── telemetry.py
│   │       │   │   ├── user.py
│   │       │   │   └── workflow.py
│   │       │   ├── base.py
│   │       │   ├── guards.py
│   │       │   └── session.py
│   │       │
│   │       ├── schemas/
│   │       │   ├── agent_outputs.py
│   │       │   ├── agents.py
│   │       │   ├── ai_providers.py
│   │       │   ├── approvals.py
│   │       │   ├── auth.py
│   │       │   ├── health.py
│   │       │   ├── knowledge.py
│   │       │   ├── memories.py
│   │       │   ├── observability.py
│   │       │   ├── orchestration.py
│   │       │   ├── payload_limits.py
│   │       │   ├── planning.py
│   │       │   └── workflows.py
│   │       │
│   │       ├── services/
│   │       │   ├── providers/
│   │       │   │   ├── base.py
│   │       │   │   ├── groq_provider.py
│   │       │   │   ├── ollama_provider.py
│   │       │   │   ├── openai_provider.py
│   │       │   │   └── provider_manager.py
│   │       │   │
│   │       │   ├── agent_memory.py
│   │       │   ├── agent_registry.py
│   │       │   ├── agent_state.py
│   │       │   ├── approval_service.py
│   │       │   ├── auth_otp.py
│   │       │   ├── document_processing.py
│   │       │   ├── email.py
│   │       │   ├── embeddings.py
│   │       │   ├── execution.py
│   │       │   ├── execution_factory.py
│   │       │   ├── handlers.py
│   │       │   ├── knowledge_base.py
│   │       │   ├── llm.py
│   │       │   ├── memory_safety.py
│   │       │   ├── ollama_generation.py
│   │       │   ├── orchestration_evaluation.py
│   │       │   ├── orchestrator.py
│   │       │   ├── planner.py
│   │       │   ├── planner_evaluation.py
│   │       │   ├── rag.py
│   │       │   ├── specialized_agents.py
│   │       │   ├── task_runner.py
│   │       │   ├── telemetry.py
│   │       │   └── tool_registry.py
│   │       │
│   │       └── main.py
│   │
│   ├── tests/
│   │   ├── integration/
│   │   │   ├── db/
│   │   │   ├── test_agent_memory_pgvector.py
│   │   │   ├── test_health_real_db.py
│   │   │   ├── test_knowledge_pgvector.py
│   │   │   └── test_workflow_execution.py
│   │   │
│   │   ├── smoke/
│   │   │   └── test_health.py
│   │   │
│   │   ├── unit/
│   │   │   ├── test_agent_memory.py
│   │   │   ├── test_agent_registry.py
│   │   │   ├── test_auth_otp.py
│   │   │   ├── test_document_processing.py
│   │   │   ├── test_embeddings.py
│   │   │   ├── test_orchestrator.py
│   │   │   ├── test_provider_manager.py
│   │   │   ├── test_rag.py
│   │   │   ├── test_security.py
│   │   │   ├── test_task_runner.py
│   │   │   ├── test_telemetry.py
│   │   │   └── test_tool_registry.py
│   │   │
│   │   └── conftest.py
│   │
│   ├── .python-version
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── uv.lock
│
├── docker/
│   └── postgres/
│       └── init/
│           └── 01-create-test-db.sql
│
├── frontend/
│   ├── public/
│   │   ├── auth-waves.svg
│   │   └── favicon.svg
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx
│   │   │   ├── AppRouter.tsx
│   │   │   ├── providers.tsx
│   │   │   ├── query-client.ts
│   │   │   └── router.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── navbar/
│   │   │   ├── sidebar/
│   │   │   └── ui/
│   │   │
│   │   ├── features/
│   │   │   ├── agents/
│   │   │   ├── analytics/
│   │   │   ├── approvals/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── invitations/
│   │   │   ├── knowledge/
│   │   │   ├── memory/
│   │   │   ├── settings/
│   │   │   └── workflows/
│   │   │
│   │   ├── layouts/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── types/
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   │
│   ├── .nvmrc
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── vitest.config.ts
│
├── .env.example
├── .gitignore
├── .python-version
├── architecture.txt
├── docker-compose.yml
├── folder_structure.txt
├── Makefile
└── README.md
```

## 🧭 1. Backend Organization

The backend follows a modular Python package structure.

| Directory | Responsibility |
|---|---|
| `api/` | Versioned REST endpoints and API dependencies |
| `core/` | Configuration, authentication, security, middleware and logging |
| `db/` | SQLAlchemy models, database sessions and integrity guards |
| `schemas/` | Pydantic request and response contracts |
| `services/` | Application, workflow, AI, knowledge, memory and telemetry logic |
| `tests/` | Unit, integration and smoke tests |
| `migrations/` | Version-controlled database schema changes |
| `scripts/` | Administrative and development utilities |

## 🎨 2. Frontend Organization

The frontend follows a feature-oriented React and TypeScript structure.

| Directory | Responsibility |
|---|---|
| `app/` | Application entry, router and providers |
| `components/` | Shared UI components |
| `features/` | Feature-specific application interfaces |
| `layouts/` | Authentication and workspace layouts |
| `lib/` | Shared API and utility functions |
| `pages/` | Application-level pages |
| `services/` | API integration and feature services |
| `styles/` | Global application styles |
| `types/` | Shared TypeScript types |

## 🧪 3. Testing Organization

Backend tests are grouped by validation purpose.

| Directory | Purpose |
|---|---|
| `tests/unit/` | Isolated service, validation and application logic tests |
| `tests/integration/` | Database-backed and service integration tests |
| `tests/smoke/` | Basic application readiness checks |

Frontend tests are maintained alongside the relevant frontend source modules.

## 🐳 4. Infrastructure Organization

The repository includes:

- `docker-compose.yml` for PostgreSQL and pgvector infrastructure.
- `docker/postgres/init/` for initial PostgreSQL database setup.
- `.env.example` for environment configuration.
- `Makefile` for development commands.
- `architecture.txt` for the platform architecture overview.

## 🖼️ 5. README Visual Assets

The following directory is used for the project screenshots being added to this README:

```text
docs/
└── screenshots/
    ├── agentops-overview.png
    ├── dashboard.png
    ├── workflow-builder.png
    ├── workflow-execution.png
    ├── knowledge-base.png
    ├── knowledge-search.png
    ├── agent-analysis.png
    ├── agent-report.png
    ├── agent-memory.png
    ├── provider-settings.png
    └── analytics.png
```

Only add files that have actually been captured and saved to the repository.

**The screenshot directory is a documentation-assets location being added for the README; it is not listed in the currently published `folder_structure.txt` snapshot.**

### 💡 Repository Design Philosophy

The repository structure separates application responsibilities and keeps the codebase organized around its major technical capabilities.

This supports maintainability, testing, independent feature development, and future extension of the platform.

---

# 🚀 Installation Guide

This guide explains how to clone, configure, and run AgentOps-OS locally.

The development environment uses Docker Compose for PostgreSQL infrastructure, FastAPI for backend services, and React with Vite for the frontend application.

The setup instructions use **Windows PowerShell** as the primary development environment.

## 🧰 1. Prerequisites

Install the following tools before starting.

| Requirement | Version / Purpose |
|---|---|
| Git | Repository cloning and version control |
| Python | 3.12 or newer |
| uv | Python environment and dependency management |
| Node.js | 22.12 or newer |
| npm | Frontend package management |
| Docker Desktop | Local database infrastructure |
| Docker Compose | PostgreSQL service management |
| Ollama | Optional local LLM and embedding runtime |

**Recommended versions:**

- Python 3.12.
- Node.js 22.16.0.
- PostgreSQL 16 with pgvector.
- Docker Compose v2 or newer.

## 📥 2. Clone the Repository

Open PowerShell and run:

```powershell
git clone https://github.com/vivekgadhe/AgentOps-OS.git

cd AgentOps-OS
```

## ⚙️ 3. Configure Environment Variables

Create the root `.env` file using the provided example.

```powershell
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Open the `.env` file and verify the database configuration.

```env
APP_ENV=dev
LOG_LEVEL=INFO
LOG_FORMAT=console

POSTGRES_USER=agentops
POSTGRES_PASSWORD=agentops
POSTGRES_DB=agentops
POSTGRES_PORT=5433

DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops

TEST_DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops_test

JWT_SECRET=dev-insecure-secret-change-me
```

**Important:**

- `POSTGRES_PORT` controls the host port exposed by Docker Compose.
- `DATABASE_URL` must use the same port.
- The `+psycopg` portion of the database URL selects the Psycopg 3 driver.
- The development JWT placeholder must not be used for production.
- Never commit `.env` or private credentials to GitHub.

The example uses port `5433` to avoid conflicts with a PostgreSQL service already using the default port `5432`.

## 🐳 4. Start PostgreSQL with Docker Compose

From the repository root, start the database service.

```powershell
docker compose up -d --wait db
```

Check the service:

```powershell
docker compose ps
```

The expected database service is:

```text
db
```

The database image includes PostgreSQL 16 and pgvector.

**Important:** Docker Compose currently starts the database infrastructure. The FastAPI backend and React frontend are run separately during local development.

## 🐍 5. Set Up the Python Environment

Install Python 3.12 using uv if it is not already available.

```powershell
uv python install 3.12
```

Verify the installed version:

```powershell
uv python list
```

Navigate to the backend directory:

```powershell
cd backend
```

Install backend dependencies, including development and testing dependencies:

```powershell
uv sync --extra dev
```

This command creates the Python virtual environment and installs the dependencies declared in `pyproject.toml` and `uv.lock`.

## 🗄️ 6. Apply Database Migrations

With PostgreSQL running and the backend environment configured, apply the database migrations.

```powershell
uv run alembic upgrade head
```

Verify the current migration revision:

```powershell
uv run alembic current
```

The expected latest migration revision in the current repository is:

```text
0008 (head)
```

The migration system manages the schema for authentication, workflows, knowledge, AI providers, approvals, memory, and telemetry.

**Database safety:** Run migrations only against the intended development database. The integration-test setup uses a separate database and includes safeguards against running tests against an ordinary development database.

## 📧 7. Configure Email OTP Registration

Email OTP registration requires a working SMTP configuration.

Add the following settings to the root `.env` file when testing registration and email verification.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-smtp-app-password

SMTP_FROM_EMAIL=your-email@example.com
SMTP_FROM_NAME=AgentOps-OS

SMTP_STARTTLS=true
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=5
OTP_RESEND_COOLDOWN_SECONDS=60
```

Generate an OTP pepper for local configuration:

```powershell
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Add the generated value to `.env`:

```env
OTP_PEPPER=replace-with-generated-random-value
```

**Configuration notes:**

- `SMTP_HOST` and `SMTP_FROM_EMAIL` must be configured together.
- `SMTP_USERNAME` and `SMTP_PASSWORD` must be configured together.
- Use the SMTP credentials appropriate for your email provider.
- Never publish SMTP credentials or OTP secrets.
- Production requires SMTP configuration and an OTP pepper.

Email OTP registration cannot be fully demonstrated until the SMTP service successfully delivers verification messages.

## 🦙 8. Configure Ollama for Local AI Models

Ollama is optional for running the basic application, but it is required for local model functionality.

Install and start Ollama on your machine.

Verify the service:

```powershell
ollama --version
```

Pull the local language model used during development:

```powershell
ollama pull qwen3.5:0.8b
```

Pull the embedding model:

```powershell
ollama pull embeddinggemma
```

List installed models:

```powershell
ollama list
```

The backend configuration uses the following defaults:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen3.5:0.8b
OLLAMA_EMBEDDING_MODEL=embeddinggemma
```

The local model runtime is accessed through:

```text
http://localhost:11434
```

The local language model is used for supported generation operations, while the embedding model supports the knowledge and vector retrieval pipeline.

Hosted provider integrations are optional for local Ollama-based experimentation.

## ▶️ 9. Start the FastAPI Backend

From the `backend` directory:

```powershell
uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

### Verify Backend Health

Open another PowerShell terminal and run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

A healthy response indicates that the backend is running and its readiness check has succeeded.

## ⚛️ 10. Set Up the React Frontend

Open a new PowerShell terminal.

Navigate to the frontend directory:

```powershell
cd AgentOps-OS/frontend
```

Install dependencies from the committed lockfile:

```powershell
npm ci
```

Verify the Node.js version:

```powershell
node --version
```

The frontend requires Node.js 22.12 or newer.

The repository includes an `.nvmrc` file selecting Node.js 22.16.0.

## 🌐 11. Start the Frontend Development Server

Run:

```powershell
npm run dev
```

The frontend will be available at:

```text
http://127.0.0.1:5173
```

The Vite development configuration forwards `/api` requests to:

```text
http://127.0.0.1:8000
```

The backend should therefore be running while using frontend features that depend on API communication.

## 🔐 12. Bootstrap an Administrator Account

For administrative access, the backend includes a user-management CLI.

Open a terminal in the backend directory:

```powershell
cd AgentOps-OS/backend
```

Run:

```powershell
uv run python scripts/manage_users.py bootstrap-admin --email your-email@example.com
```

Follow the CLI prompts to complete administrator setup.

To list existing user accounts:

```powershell
uv run python scripts/manage_users.py list-users
```

Public self-service registration separately creates ordinary operator accounts after successful email verification.

## 🧪 13. Run Frontend Verification

From the frontend directory:

```powershell
npm run typecheck
```

Run frontend tests:

```powershell
npm test
```

Create the production build:

```powershell
npm run build
```

Or execute the combined check:

```powershell
npm run check
```

## 🧪 14. Run Backend Verification

From the backend directory:

### Run Unit and Non-Integration Tests

```powershell
uv run pytest -m "not integration"
```

### Run Integration Tests

Make sure the PostgreSQL test database is available.

```powershell
$env:AGENTOPS_REQUIRE_DB = "1"

uv run pytest -m integration
```

The test configuration refuses to run integration tests against a database whose name does not meet the required test-database safeguards.

### Run the Complete Test Suite

```powershell
uv run pytest
```

### Run Ruff

```powershell
uv run ruff check src tests
```

### Check Formatting

```powershell
uv run ruff format --check src tests
```

### Run mypy

```powershell
uv run mypy src
```

## ✅ 15. Access the Application

After the database, backend, and frontend have started, open:

| Component | Local Address |
|---|---|
| AgentOps-OS Frontend | http://127.0.0.1:5173 |
| FastAPI Backend | http://127.0.0.1:8000 |
| Swagger API Docs | http://127.0.0.1:8000/docs |
| ReDoc API Docs | http://127.0.0.1:8000/redoc |
| Backend Readiness | http://127.0.0.1:8000/api/v1/health/ready |
| Ollama Runtime | http://localhost:11434 |

## 🛠️ 16. Troubleshooting

### PostgreSQL Port Already in Use

If the default PostgreSQL port is occupied, change `POSTGRES_PORT` in the root `.env` file.

For example:

```env
POSTGRES_PORT=5433
DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops
TEST_DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops_test
```

The port in the database URLs must match the Docker Compose host port.

### Database Is Not Ready

Check the container:

```powershell
docker compose ps
```

Inspect database logs:

```powershell
docker compose logs db
```

### Backend Cannot Connect to PostgreSQL

Verify:

- Docker database service is running.
- `DATABASE_URL` contains the correct host port.
- Database username and password match the Docker configuration.
- The database is healthy.

### Frontend Cannot Reach Backend

Verify:

- FastAPI is running on port `8000`.
- Frontend Vite is running on port `5173`.
- The Vite `/api` proxy target is configured correctly.

The default proxy target is:

```text
http://127.0.0.1:8000
```

### Local Model Is Unavailable

Verify Ollama:

```powershell
ollama list
```

Check that the Ollama service is running and that the configured model has been downloaded.

### Email OTP Is Not Received

Verify:

- SMTP host and port.
- SMTP username and password.
- Sender email address.
- STARTTLS configuration.
- Email provider security requirements.

## ⚠️ Development Environment Notes

- The root `.env` file contains local credentials and must never be committed.
- Docker Compose currently provides the database service, not a complete containerized application deployment.
- Backend and frontend are started independently during local development.
- Local Ollama inference depends on available machine resources.
- Integration tests use a separate, guarded test database.
- Use strong secrets and production-specific configuration before any production deployment.

---

### 🎉 Installation Complete

AgentOps-OS is now ready for local development.

You can explore its dashboard, configure AI providers, create workflows, manage knowledge documents, interact with specialized AI capabilities, work with persistent memory, and inspect available operational information.

---

# ⚙️ Environment Configuration

AgentOps-OS uses environment variables to manage application configuration, database connectivity, authentication, email delivery, AI provider integrations, knowledge processing, persistent memory, and observability.

The repository includes a root `.env.example` file containing the primary development configuration.

The application uses Pydantic Settings to load and validate configuration values.

## 📄 1. Environment File Structure

The repository uses the following configuration files:

| File | Purpose |
|---|---|
| `.env.example` | Example configuration without personal credentials |
| `.env` | Local application and database configuration |
| `backend/.env` | Optional backend-specific configuration |
| `frontend/.env.local` | Optional Vite frontend environment overrides |

The backend settings load configuration from the repository-root `.env` and the backend-local `.env`.

Real environment variables take precedence over environment files.

**Important:** Never commit your actual `.env` file or private credentials to GitHub.

## 📥 2. Create the Environment File

From the repository root:

```powershell
Copy-Item .env.example .env
```

Open `.env` and update the settings according to your local environment.

## 🗄️ 3. Core Application and Database Variables

The following variables are provided in the repository's `.env.example`.

| Variable | Description | Development Example |
|---|---|---|
| `APP_ENV` | Application environment | `dev` |
| `LOG_LEVEL` | Application logging level | `INFO` |
| `LOG_FORMAT` | Logging output format | `console` |
| `POSTGRES_USER` | PostgreSQL username | `agentops` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `agentops` |
| `POSTGRES_DB` | Primary database name | `agentops` |
| `POSTGRES_PORT` | Host port exposed by Docker Compose | `5433` |
| `DATABASE_URL` | Application database connection | PostgreSQL URL |
| `TEST_DATABASE_URL` | Dedicated integration-test database | `agentops_test` |
| `JWT_SECRET` | Secret used for access-token signing | Development placeholder |

## 🔐 4. Authentication and Email Configuration

The backend supports email-based OTP registration, administrator invitations, and password recovery.

The following settings control SMTP delivery and OTP behavior.

| Variable | Description | Default |
|---|---|---|
| `SMTP_HOST` | SMTP server hostname | Not configured |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP authentication username | Not configured |
| `SMTP_PASSWORD` | SMTP authentication password | Not configured |
| `SMTP_FROM_EMAIL` | Sender email address | Not configured |
| `SMTP_FROM_NAME` | Display name of sender | `AgentOps-OS` |
| `SMTP_STARTTLS` | Enable STARTTLS | `true` |
| `SMTP_TIMEOUT_S` | SMTP connection timeout | `15` |
| `OTP_PEPPER` | Secret used for OTP protection | Not configured |
| `OTP_EXPIRY_MINUTES` | OTP expiration period | `10` |
| `OTP_MAX_ATTEMPTS` | Maximum verification attempts | `5` |
| `OTP_RESEND_COOLDOWN_SECONDS` | Resend cooldown | `60` |
| `OTP_MAX_REQUESTS_PER_HOUR` | Maximum OTP requests per hour | `5` |

SMTP configuration is required for actual email delivery.

## 🤖 5. AI and LLM Configuration

The application supports hosted AI integrations and local Ollama model execution.

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Optional OpenAI API credential for the environment-based integration | Not configured |
| `OPENAI_MODEL` | Model used by the environment-based integration | `gpt-5.5` |
| `LLM_TIMEOUT_S` | Hosted LLM request timeout | `30` |
| `OLLAMA_BASE_URL` | Ollama service address | `http://localhost:11434` |
| `OLLAMA_CHAT_MODEL` | Local language model | `qwen3.5:0.8b` |
| `OLLAMA_EMBEDDING_MODEL` | Local embedding model | `embeddinggemma` |
| `OLLAMA_TIMEOUT_S` | Ollama request timeout | `180` |
| `AI_PROVIDER_TIMEOUT_S` | Configured provider timeout | `60` |
| `AI_CREDENTIAL_ENCRYPTION_KEY` | Encryption key for stored hosted-provider credentials | Not configured |

The provider-management interface supports OpenAI, Groq, and Ollama.

Hosted-provider credentials configured through the provider-management interface are encrypted before being stored in PostgreSQL.

`AI_CREDENTIAL_ENCRYPTION_KEY` must be configured before saving hosted-provider API credentials.

Ollama does not require a hosted-provider API key.

## 📚 6. Knowledge Processing Configuration

The following settings control document ingestion and processing.

| Variable | Description | Default |
|---|---|---:|
| `KNOWLEDGE_MAX_UPLOAD_BYTES` | Maximum upload size in bytes | `10485760` |
| `KNOWLEDGE_MAX_PDF_PAGES` | Maximum PDF pages | `200` |
| `KNOWLEDGE_CHUNK_SIZE_CHARS` | Document chunk size | `1200` |
| `KNOWLEDGE_CHUNK_OVERLAP_CHARS` | Chunk overlap | `200` |
| `KNOWLEDGE_MAX_CHUNKS_PER_DOCUMENT` | Maximum chunks per document | `5000` |

The chunk overlap must be smaller than the configured chunk size.

## 🧠 7. Agent Memory Configuration

| Variable | Description | Default |
|---|---|---:|
| `MEMORY_MAX_CONTENT_CHARS` | Maximum memory content length | `5000` |
| `MEMORY_DEFAULT_TTL_DAYS` | Default memory lifetime | `90` |
| `MEMORY_AUTO_CAPTURE_RAG` | Enable automatic RAG memory capture | `false` |
| `MEMORY_RETRIEVAL_TOP_K` | Maximum retrieved memories | `5` |

Automatic memory capture is disabled by default to avoid retaining prompts and generated responses without explicit configuration.

## 📊 8. Observability Configuration

| Variable | Description | Default |
|---|---|---|
| `OBSERVABILITY_ENABLED` | Enable observability instrumentation | `true` |
| `TELEMETRY_RETENTION_DAYS` | Telemetry retention period | `90` |

Telemetry is designed to store operational metadata rather than model prompts or generated outputs.

## 📝 9. Example Optional Configuration

The following settings can be added to the root `.env` when the corresponding capabilities are required.

```env
# =====================================
# SMTP / Email OTP
# =====================================

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-app-password
SMTP_FROM_EMAIL=your-email@example.com
SMTP_FROM_NAME=AgentOps-OS
SMTP_STARTTLS=true

OTP_PEPPER=replace-with-a-random-secret

# =====================================
# Local Ollama
# =====================================

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen3.5:0.8b
OLLAMA_EMBEDDING_MODEL=embeddinggemma

# =====================================
# Hosted Provider Credential Encryption
# =====================================

AI_CREDENTIAL_ENCRYPTION_KEY=replace-with-a-valid-fernet-key

# =====================================
# Persistent Memory
# =====================================

MEMORY_AUTO_CAPTURE_RAG=false

# =====================================
# Observability
# =====================================

OBSERVABILITY_ENABLED=true
TELEMETRY_RETENTION_DAYS=90
```

## 🔑 10. Generate Secure Application Secrets

Generate a random JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate an OTP pepper:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Generate a valid Fernet encryption key after installing the backend dependencies:

```powershell
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use the generated values in the root `.env` file.

**Security Requirements:**

- A non-development JWT secret must contain at least 32 characters and must not use the development placeholder.
- Production requires SMTP host, sender email, and OTP pepper configuration.
- Hosted-provider API credentials must be encrypted using a valid Fernet key.
- Never expose passwords, OTP secrets, JWT secrets, or API credentials in screenshots or GitHub commits.

## ⚠️ 11. Development and Production Configuration

| Configuration | Development | Production |
|---|---|---|
| `APP_ENV` | `dev` | `prod` |
| JWT secret | Development placeholder permitted | Strong random secret required |
| SMTP | Optional until email functionality is used | Required |
| OTP pepper | Optional | Required |
| Database URL | Local development database | Secure deployment database |
| Logging | Console | Deployment-specific configuration |
| API documentation | Available | Disabled by default |
| Provider credentials | Local development configuration | Secure credential management |

The application validates configuration during startup and rejects several unsafe production configurations.

### 💡 Configuration Philosophy

AgentOps-OS keeps configuration separate from application source code to improve portability, maintainability, and credential security.

---

# 🗄️ Database Setup

AgentOps-OS uses PostgreSQL as its primary relational database and pgvector for vector-based knowledge retrieval and persistent memory operations.

The database infrastructure is managed through Docker Compose, while database schema changes are managed through Alembic migrations.

## 🐘 1. Database Technology

| Component | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Vector Extension | pgvector |
| Container Image | `pgvector/pgvector:0.8.7-pg16-bookworm` |
| ORM | SQLAlchemy 2 |
| Database Driver | Psycopg 3 |
| Migration Tool | Alembic |

## 🐳 2. PostgreSQL Infrastructure

The repository's `docker-compose.yml` defines the PostgreSQL database service.

The service includes:

- PostgreSQL 16 with pgvector.
- Environment-based database credentials.
- Configurable host port.
- Persistent database storage.
- PostgreSQL initialization scripts.
- Container health checking.

## 🚀 3. Start the Database

From the repository root:

```powershell
docker compose up -d --wait db
```

Check the service:

```powershell
docker compose ps
```

Inspect database logs:

```powershell
docker compose logs db
```

The database is exposed on the host port specified by `POSTGRES_PORT` in `.env`.

The default repository development configuration uses port `5433`.

## 🔌 4. Database Connection Configuration

The root `.env` contains the database connection information.

```env
POSTGRES_USER=agentops
POSTGRES_PASSWORD=agentops
POSTGRES_DB=agentops
POSTGRES_PORT=5433

DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops

TEST_DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops_test
```

The application requires the SQLAlchemy connection URL to use the Psycopg 3 driver:

```text
postgresql+psycopg://
```

The host port in `DATABASE_URL` must match the Docker Compose host port.

## 🧪 5. Integration Test Database

The repository includes a separate PostgreSQL integration-test database.

Its default configuration is:

```env
TEST_DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops_test
```

The integration-test database name must end in:

```text
_test
```

The PostgreSQL initialization script creates the test database when the database volume is initialized for the first time.

The backend test configuration also checks the target database before running integration tests.

**Important:** If you change the initialization script after an existing PostgreSQL volume has already been created, Docker's initialization scripts are not automatically rerun for that existing volume.

## 🧬 6. pgvector Extension

pgvector provides vector data storage and similarity-search functionality within PostgreSQL.

AgentOps-OS uses vector operations for:

- Knowledge document embeddings.
- Semantic knowledge retrieval.
- Persistent memory embeddings.
- Similarity-based memory search.

The PostgreSQL container image includes pgvector support, and database migrations manage the application's required schema.

## 🔄 7. Run Alembic Migrations

Navigate to the backend directory:

```powershell
cd backend
```

Install backend dependencies if not already installed:

```powershell
uv sync --extra dev
```

Apply all database migrations:

```powershell
uv run alembic upgrade head
```

This brings the development database schema to the latest migration revision.

## 🔍 8. Verify the Current Migration

Run:

```powershell
uv run alembic current
```

The latest migration in the current repository is:

```text
0008 (head)
```

The migration history includes:

| Revision | Description |
|---|---|
| `0001_initial_schema` | Initial application schema |
| `0002_knowledge_base` | Document and vector storage |
| `0003_ai_providers_and_approvals` | Provider configuration and approvals |
| `0004_persistent_agent_memory` | Persistent memory |
| `0005_observability_telemetry` | Operational telemetry |
| `0006_auth_action_tokens` | Authentication action tokens |
| `0007_email_otp_security` | Email OTP security |
| `0008_public_registration_otp` | Public registration verification |

## 🛡️ 9. Migration Safety

AgentOps-OS uses database-target validation before executing migrations.

The Alembic configuration deliberately does not contain a hard-coded database URL.

Instead, migrations obtain the database connection through application settings and verify the actual target database before applying changes.

The migration setup also rejects offline SQL generation because the live database must be inspected for safety.

**Important database practices:**

- Verify the active `.env` before running migrations.
- Do not run development migrations against production.
- Maintain a separate integration-test database.
- Keep database credentials outside source control.
- Back up important data before applying schema changes.

## 💡 Database Design Summary

The database provides persistent storage for:

- User accounts and authentication.
- Workflow runs and task executions.
- Task dependency relationships.
- Knowledge documents and chunks.
- Vector embeddings.
- Persistent agent memories.
- Human approval requests.
- AI provider configurations.
- Telemetry and operational events.

### Database Architecture

**PostgreSQL + SQLAlchemy + Alembic + pgvector**

Together, these technologies provide the relational persistence, schema versioning, and vector retrieval foundations used by AgentOps-OS.

---

# 🦙 Ollama Setup — Local LLM and Embedding Models

AgentOps-OS supports local AI model integration through Ollama.

Ollama provides a runtime for executing compatible language models and embedding models on a local machine.

This allows developers to experiment with supported AI functionality without depending exclusively on paid hosted inference APIs.

## 🧩 1. Ollama Integration

AgentOps-OS uses Ollama for two different AI operations:

| Model Type | Purpose |
|---|---|
| Language Model | Generates AI responses and structured outputs |
| Embedding Model | Converts text into vector representations |

These models serve different responsibilities within the application.

## 💻 2. Install and Verify Ollama

Install Ollama on your development machine.

After installation, open PowerShell and verify the command:

```powershell
ollama --version
```

Confirm that the local Ollama service is accessible:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

The default local Ollama runtime address is:

```text
http://localhost:11434
```

## 🤖 3. Download the Language Model

AgentOps-OS used the following local model during development:

```powershell
ollama pull qwen3.5:0.8b
```

The model is configured as:

```env
OLLAMA_CHAT_MODEL=qwen3.5:0.8b
```

It is used for supported language-generation operations.

## 🧬 4. Download the Embedding Model

Download the local embedding model:

```powershell
ollama pull embeddinggemma
```

Configure it using:

```env
OLLAMA_EMBEDDING_MODEL=embeddinggemma
```

The embedding model is used by:

- Knowledge document indexing.
- Semantic knowledge search.
- RAG query embedding.
- Persistent memory embedding.
- Memory retrieval and search.

## 📋 5. Verify Installed Models

Run:

```powershell
ollama list
```

The expected development models are:

```text
qwen3.5:0.8b
embeddinggemma
```

Your local installation may display the embedding model with an explicit tag such as `embeddinggemma:latest`.

The model names configured in the backend must match the installed model identifiers.

## ⚙️ 6. Configure Ollama in `.env`

Add or verify these settings in the root `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_CHAT_MODEL=qwen3.5:0.8b

OLLAMA_EMBEDDING_MODEL=embeddinggemma

OLLAMA_TIMEOUT_S=180
```

Restart the backend after changing environment variables.

## 🔌 7. Configure Ollama in AgentOps-OS

<!-- Screenshot: docs/screenshots/ollama-configuration.png -->

Open the application and navigate to:

```text
Settings → AI Providers → Ollama
```

Configure:

| Setting | Value |
|---|---|
| Provider | Ollama |
| Base URL | `http://localhost:11434` |
| Chat Model | `qwen3.5:0.8b` |
| Provider Type | Local |

Save the configuration and use the provider connectivity test.

The provider-management API supports Ollama configuration using a permitted local runtime URL.

## 🧪 8. Validate the Integration

Check Ollama's installed models:

```powershell
ollama list
```

Check whether the service is responding:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Then use the AgentOps-OS provider settings interface to test the configured provider.

A successful provider test confirms that the application can communicate with the configured model.

## 🔄 9. Ollama Integration Architecture

```mermaid
flowchart TD
    A([AgentOps-OS])
    B[FastAPI Backend]
    C[Ollama Client]
    D{Model Operation}

    E[Qwen Language Model]
    F[EmbeddingGemma]
    G[Generated Response]
    H[Document or Query Vector]

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F

    E --> G
    F --> H
```

## ⚠️ 10. Troubleshooting

### Ollama Command Not Recognized

Verify that Ollama is installed and that its executable is available in the system PATH.

### Ollama Service Is Unavailable

Check the local service:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### Model Not Found

Verify installed model identifiers:

```powershell
ollama list
```

Pull any missing model:

```powershell
ollama pull qwen3.5:0.8b
ollama pull embeddinggemma
```

### Embedding Requests Fail

Verify:

- Ollama is running.
- The embedding model is installed.
- `OLLAMA_BASE_URL` is correct.
- `OLLAMA_EMBEDDING_MODEL` matches the installed model.
- The backend has been restarted after configuration changes.

## 💡 Local AI Development Philosophy

Ollama gives AgentOps-OS a local-model execution option.

This supports experimentation with LLM integration and vector embeddings without requiring a paid hosted API as the default development environment.

Actual model performance depends on available hardware, model size, and workload.

---

# ▶️ Running the Application

AgentOps-OS consists of three main components during local development:

1. PostgreSQL database infrastructure.
2. FastAPI backend application.
3. React frontend application.

The database is started through Docker Compose, while the backend and frontend are run independently.

## 🐳 1. Start PostgreSQL

Open Terminal 1 in the repository root:

```powershell
docker compose up -d --wait db
```

Verify the database:

```powershell
docker compose ps
```

The database should be running before starting the backend.

## 🐍 2. Start the Backend

Open Terminal 2.

Navigate to the backend directory:

```powershell
cd AgentOps-OS/backend
```

Install dependencies if necessary:

```powershell
uv sync --extra dev
```

Apply database migrations:

```powershell
uv run alembic upgrade head
```

Start FastAPI:

```powershell
uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000
```

The backend is available at:

```text
http://127.0.0.1:8000
```

### Backend Health Verification

Open another PowerShell terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/live
```

Check database readiness:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

## ⚛️ 3. Start the Frontend

Open Terminal 3.

Navigate to the frontend directory:

```powershell
cd AgentOps-OS/frontend
```

Install frontend dependencies:

```powershell
npm ci
```

Start the Vite development server:

```powershell
npm run dev
```

The frontend is available at:

```text
http://127.0.0.1:5173
```

## 🌐 4. Frontend-to-Backend Communication

During development, the Vite server proxies API requests.

| Component | Address |
|---|---|
| Frontend | `http://127.0.0.1:5173` |
| Backend | `http://127.0.0.1:8000` |
| API Prefix | `/api/v1` |

The default proxy target is:

```text
http://127.0.0.1:8000
```

It can be overridden using:

```env
VITE_BACKEND_PROXY_TARGET=http://127.0.0.1:8000
```

This variable belongs to the frontend's Vite environment configuration.

## 🔐 5. Access AgentOps-OS

Open your browser:

```text
http://127.0.0.1:5173
```

Use an existing account or complete public registration after configuring SMTP.

For administrator access, use the backend user-management CLI to bootstrap an administrator account.

## 📚 6. Access API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

These documentation interfaces are available in development mode and are disabled when `APP_ENV=prod`.

## 🛑 7. Stop the Application

Stop the backend and frontend by pressing:

```text
Ctrl + C
```

Stop the PostgreSQL container from the repository root:

```powershell
docker compose down
```

The default command preserves the named database volume.

To remove the database volume as well, Docker provides a separate volume-removal option. Be careful: removing the volume permanently deletes the local database data.

## 🧭 8. Local Development Startup Summary

```text
Terminal 1
└── AgentOps-OS/
    └── docker compose up -d --wait db

Terminal 2
└── AgentOps-OS/backend/
    └── uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000

Terminal 3
└── AgentOps-OS/frontend/
    └── npm run dev
```

## 💡 Local Application Architecture

```mermaid
flowchart TB
    BROWSER([Web Browser])

    FRONTEND["React + Vite<br/>127.0.0.1:5173"]
    BACKEND["FastAPI<br/>127.0.0.1:8000"]
    DATABASE[("PostgreSQL + pgvector<br/>127.0.0.1:5433")]
    OLLAMA["Optional Ollama Runtime<br/>localhost:11434"]

    BROWSER --> FRONTEND
    FRONTEND -->|"/api/* proxy"| BACKEND
    BACKEND --> DATABASE
    BACKEND --> OLLAMA
```

*Ollama is an optional local AI runtime. The application can also use configured hosted providers.*

### ✅ Application Startup Complete

Once the database, backend, and frontend are running, AgentOps-OS is ready for local development and feature exploration.

---

# 📡 API Documentation

AgentOps-OS provides a versioned REST API built using FastAPI.

The API layer exposes application functionality for authentication, workflow orchestration, knowledge management, persistent memory, AI provider configuration, human approvals, and operational observability.

The backend uses Pydantic schemas to validate requests and structure API responses.

## 📖 1. Interactive API Documentation

FastAPI automatically generates OpenAPI documentation from the registered application routes.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides:

- Available API operations.
- Request parameters.
- Request body schemas.
- Response schemas.
- Authentication support.
- Interactive API testing.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

ReDoc provides an alternative documentation interface for exploring API contracts.

### OpenAPI Specification

```text
http://127.0.0.1:8000/openapi.json
```

The OpenAPI JSON document describes the available API operations and their request and response structures.

**Note:** Swagger UI, ReDoc, and the OpenAPI endpoint are enabled in development mode and disabled when `APP_ENV=prod`.

## 🔗 2. API Base URL

The default local API base URL is:

```text
http://127.0.0.1:8000/api/v1
```

All versioned application API routes are registered under:

```text
/api/v1
```

## 🧩 3. API Modules

AgentOps-OS organizes its API endpoints into the following major modules.

| API Module | Base Path | Responsibility |
|---|---|---|
| Health | `/health` | Liveness and database readiness |
| Authentication | `/auth` | Registration, login and account access |
| Workflows | `/runs` | Workflow planning and execution |
| Knowledge | `/knowledge` | Document management, semantic search and RAG |
| Agent Memory | `/memories` | Persistent memory management |
| AI Providers | `/ai-providers` | Provider configuration and connectivity testing |
| Approvals | `/approvals` | Human approval requests and decisions |
| Observability | `/observability` | Operational analytics and telemetry |

## ❤️ 4. Health APIs

Health endpoints provide basic service and database readiness information.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/live` | Checks whether the application process is running |
| GET | `/health/ready` | Checks application and database readiness |

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

A healthy database readiness response is structured as:

```json
{
  "status": "ok",
  "db": "up"
}
```

## 🔐 5. Authentication APIs

Authentication endpoints manage account access, registration verification, and login.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/request` | Request a registration OTP |
| POST | `/auth/register` | Complete registration and create an operator account |
| POST | `/auth/login` | Authenticate an existing account |
| GET | `/auth/me` | Retrieve the authenticated user's account |
| POST | `/auth/invitations` | Optional administrator invitation |
| POST | `/auth/password-reset` | Complete password recovery |

The invitation endpoint is retained as optional compatibility functionality. Public registration does not require an administrator invitation.

## 🔄 6. Workflow APIs

Workflow endpoints provide planning, creation, execution, and retrieval functionality.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/runs/plan` | Generate and validate a workflow plan |
| POST | `/runs` | Create a workflow and its tasks |
| POST | `/runs/{run_id}/execute` | Execute an existing workflow |
| GET | `/runs/{run_id}` | Retrieve workflow information and task details |

Workflow operations use authenticated user context and ownership checks.

## 📚 7. Knowledge APIs

Knowledge endpoints manage uploaded documents and knowledge retrieval.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/knowledge/documents` | Upload and index a document |
| GET | `/knowledge/documents` | List the current user's documents |
| DELETE | `/knowledge/documents/{document_id}` | Delete an owned document |
| POST | `/knowledge/search` | Perform semantic knowledge retrieval |
| POST | `/knowledge/query` | Generate an Analysis Agent answer using retrieved knowledge |
| POST | `/knowledge/report` | Generate a Report Agent response using retrieved knowledge |

Supported document formats include PDF, TXT, and Markdown.

## 🧠 8. Agent Memory APIs

Memory endpoints provide persistent memory creation, retrieval, searching, updating, and deletion.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/memories` | Create a memory |
| GET | `/memories` | List available owned memories |
| POST | `/memories/search` | Search relevant memories |
| GET | `/memories/{memory_id}` | Retrieve a memory |
| PATCH | `/memories/{memory_id}` | Update a memory |
| DELETE | `/memories/{memory_id}` | Delete an individual memory |
| DELETE | `/memories/expired` | Purge expired memories |

Memory APIs enforce authenticated ownership boundaries.

## 🔌 9. AI Provider APIs

Provider endpoints manage supported model-provider configurations.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/ai-providers` | List configured providers |
| PUT | `/ai-providers/{provider_name}` | Create or update a provider |
| DELETE | `/ai-providers/{provider_name}` | Remove a provider configuration |
| POST | `/ai-providers/test` | Test the configured provider chain |

Supported provider identifiers:

```text
openai
groq
ollama
```

Hosted provider API credentials are encrypted before persistence.

Ollama configuration supports local model integration without requiring a hosted-provider API key.

## 🧑‍⚖️ 10. Approval APIs

Approval endpoints provide controlled access to approval-related operations.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/approvals` | List approval requests available to the current user |
| GET | `/approvals/{approval_id}` | Retrieve approval details |
| POST | `/approvals/{approval_id}/approve` | Approve a pending operation |
| POST | `/approvals/{approval_id}/reject` | Reject a pending operation |
| POST | `/approvals/{approval_id}/cancel` | Cancel an eligible pending request |

Approval decisions are subject to authorization checks.

Administrator approval and rejection actions are restricted to administrator accounts. Approved requests can resume their associated paused workflow.

## 📊 11. Observability APIs

Observability endpoints expose authenticated and owner-scoped operational analytics.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/observability/overview` | Workflow, task and LLM metrics |
| GET | `/observability/providers` | Provider and model usage information |
| GET | `/observability/agents` | Agent-related usage information |
| GET | `/observability/workflows` | Workflow execution analytics |
| GET | `/observability/events` | Structured telemetry event information |
| POST | `/observability/telemetry/purge` | Remove expired telemetry for the current user |

The analytics endpoints support date-range filtering.

Telemetry responses expose operational metadata rather than prompts or generated model content.

## 🔑 12. API Authentication

Protected API endpoints require an authenticated access token.

The login or registration flow returns an access token that the frontend uses when communicating with protected backend functionality.

Authenticated requests use the Bearer token authorization scheme.

Example:

```http
Authorization: Bearer <access_token>
```

Some endpoints additionally enforce role-based permissions and owner-scoped access.

## 🧪 13. Testing APIs Through Swagger

To explore an endpoint:

1. Start the backend application.
2. Open `http://127.0.0.1:8000/docs`.
3. Select an API group.
4. Expand the required endpoint.
5. Inspect the request schema.
6. Select **Try it out**.
7. Provide the required request information.
8. Execute the request.
9. Inspect the status code and response body.

For protected operations, authenticate using the available Swagger authorization control.

## 🏗️ 14. API Architecture

```mermaid
flowchart TD
    A([Frontend / API Client])
    B[FastAPI Application]
    C[Authentication and Dependencies]
    D[Pydantic Request Validation]
    E[Versioned API Router]

    F[Health APIs]
    G[Authentication APIs]
    H[Workflow APIs]
    I[Knowledge APIs]
    J[Memory APIs]
    K[Provider APIs]
    L[Approval APIs]
    M[Observability APIs]

    N[Application Services]
    O[(PostgreSQL + pgvector)]

    A --> B
    B --> C
    C --> D
    D --> E

    E --> F
    E --> G
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    E --> M

    G --> N
    H --> N
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N

    N --> O
```

## 💡 API Engineering Principles

The API architecture follows several important principles:

- Versioned REST API organization.
- Pydantic-based request and response validation.
- Authentication and authorization dependencies.
- Owner-scoped data access.
- Modular endpoint organization.
- Structured response schemas.
- Explicit error handling.
- OpenAPI-based documentation.

**The objective is to expose the platform's AI and operational capabilities through consistent, secure, and maintainable backend interfaces.**

---

# 🧪 Testing & Quality Assurance

AgentOps-OS follows automated software testing and code-quality practices to improve application reliability, maintainability, and correctness.

The project includes backend unit tests, database-backed integration tests, frontend automated tests, static type checking, linting, formatting checks, and production-build verification.

## 🐍 1. Backend Testing

The backend uses **pytest** as its primary testing framework.

The backend test suite is organized into three categories:

| Test Category | Purpose |
|---|---|
| Unit Tests | Validate isolated application services and business logic |
| Integration Tests | Validate database-backed and service integration behavior |
| Smoke Tests | Perform basic application and health checks |

### Backend Test Organization

```text
backend/
└── tests/
    ├── unit/
    │   ├── test_agent_memory.py
    │   ├── test_agent_registry.py
    │   ├── test_auth_otp.py
    │   ├── test_document_processing.py
    │   ├── test_embeddings.py
    │   ├── test_orchestrator.py
    │   ├── test_provider_manager.py
    │   ├── test_rag.py
    │   ├── test_security.py
    │   ├── test_task_runner.py
    │   ├── test_telemetry.py
    │   └── test_tool_registry.py
    │
    ├── integration/
    │   ├── test_agent_memory_pgvector.py
    │   ├── test_health_real_db.py
    │   ├── test_knowledge_pgvector.py
    │   └── test_workflow_execution.py
    │
    └── smoke/
        └── test_health.py
```

### Run Backend Tests

Navigate to the backend directory:

```powershell
cd backend
```

Run unit and non-integration tests:

```powershell
uv run pytest -m "not integration"
```

Run database-backed integration tests:

```powershell
uv run pytest -m integration
```

Run the complete backend test suite:

```powershell
uv run pytest
```

Integration tests require the dedicated PostgreSQL test database to be available.

The test configuration includes database-target safeguards to prevent integration tests from accidentally running against an ordinary development database.

## ⚛️ 2. Frontend Testing

The frontend uses **Vitest** for automated testing.

Frontend tests validate application modules and supporting functionality.

### Run Frontend Tests

Navigate to the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm ci
```

Run frontend tests:

```powershell
npm test
```

Run tests in watch mode:

```powershell
npm run test:watch
```

## 🔍 3. Frontend Type Checking

TypeScript helps identify incompatible data structures, incorrect component usage, and other type-related problems during development.

Run:

```powershell
npm run typecheck
```

This executes the TypeScript project type-checking command.

## 🏗️ 4. Production Build Verification

The frontend build verifies TypeScript compilation and generates the production application bundle.

Run:

```powershell
npm run build
```

The project also provides a combined frontend verification command:

```powershell
npm run check
```

This executes:

1. Type checking.
2. Frontend tests.
3. Production build.

## 🧹 5. Python Code Quality

AgentOps-OS uses Ruff and mypy to maintain Python code quality.

### Ruff Linting

```powershell
uv run ruff check src tests
```

### Ruff Formatting Check

```powershell
uv run ruff format --check src tests
```

### Format Python Files

```powershell
uv run ruff format src tests
```

### Static Type Checking

```powershell
uv run mypy src
```

These tools help maintain consistent formatting, identify common programming errors, and verify static type information.

## 🧪 6. Testing Coverage Areas

The automated tests cover important parts of the platform.

| Area | Validation Focus |
|---|---|
| Authentication | Password handling, OTP logic and authentication behavior |
| Security | Token validation, authorization and security utilities |
| Agent Registry | Agent registration and execution contracts |
| Agent Orchestration | Dependency handling and execution behavior |
| Workflow Execution | Task ordering, execution and state management |
| Tool Registry | Tool registration, input validation, output validation and authorization |
| Task Runner | Isolated execution and timeout handling |
| Knowledge Processing | Document extraction and chunking |
| Embeddings | Embedding integration and validation |
| RAG | Knowledge retrieval and context construction |
| Agent Memory | Persistent memory operations |
| Provider Manager | AI provider configuration and integration |
| Telemetry | Operational event recording |
| Database Integration | PostgreSQL and pgvector functionality |
| Frontend | Application feature and supporting module tests |

## 📋 7. Previously Recorded Development Validation

The following results were recorded during the project's local development and verification runs.

| Validation | Previously Recorded Result |
|---|---|
| Backend Non-Integration Tests | 395 passed |
| Backend Integration Tests | 24 passed |
| Total Backend Tests | 419 passed |
| Frontend Test Files | 8 passed |
| Frontend Tests | 32 passed |
| Frontend Type Checking | Passed |
| Frontend Production Build | Passed |
| Ruff Linting | Passed |
| Ruff Formatting Check | Passed |
| mypy Static Type Checking | Passed |

These are historical local validation results, not a claim of a continuously running CI pipeline.

Re-run the commands above against the current repository state before publishing updated test totals.

## ⚠️ 8. Build and Quality Notes

The previously recorded frontend production build completed successfully.

Vite also reported a large JavaScript chunk warning after minification.

The warning did not prevent the build from succeeding, but it identifies an opportunity for future bundle-size optimization.

## 💡 Quality Assurance Philosophy

AgentOps-OS uses automated testing and static analysis to improve:

- Application correctness.
- Backend service reliability.
- Database integration.
- Frontend behavior.
- Type safety.
- Code consistency.
- Maintainability.
- Reproducibility of development checks.

**The objective is to treat testing and code quality as part of the engineering process rather than as activities performed only after implementation.**

---

# ✅ Verification & Evidence

AgentOps-OS has been validated through automated backend testing, frontend testing, static analysis, production builds, database integration, and manual application-level checks.

This section documents the available verification evidence and distinguishes implementation status from demonstrated functionality.

## 🧪 1. Backend Verification

The backend has undergone unit, integration, and application-level testing.

| Verification | Result |
|---|---|
| Backend Unit Tests | 395 passed in a recorded run |
| Backend Integration Tests | 24 passed in a recorded run |
| Complete Backend Suite | 419 passed in a recorded run |
| Ruff Linting | Passed |
| Ruff Formatting | Passed |
| mypy | Passed across 78 source files in a recorded run |

## ⚛️ 2. Frontend Verification

The frontend has been validated using automated tests, TypeScript checking, and a production build.

| Verification | Result |
|---|---|
| Vitest Test Files | 8 passed |
| Frontend Tests | 32 passed |
| TypeScript Type Checking | Passed |
| Vite Production Build | Completed successfully |

## 🏗️ 3. Build Verification

The previously recorded frontend production build reported:

```text
Vite production build

2630 modules transformed.

dist/index.html       0.63 kB
CSS                   118.02 kB
JavaScript          1,119.98 kB

Build completed successfully.
```

The build reported a non-blocking warning about large JavaScript chunks.

## 🗄️ 4. Database Verification

The PostgreSQL development database was verified through Alembic migration commands.

```powershell
uv run alembic upgrade head

uv run alembic current
```

The database successfully reached:

```text
0008 (head)
```

The database-backed integration test suite was also executed successfully in the recorded development validation run.

## 🔄 5. Demonstrated Workflow Execution

<!-- Screenshot: docs/evidence/workflow-execution.png -->

A basic workflow was successfully created and executed through the running application.

The demonstrated workflow consisted of:

```text
Start
  |
  v
text_statistics
  |
  v
End
```

The execution returned the following structured result:

| Metric | Demonstrated Result |
|---|---:|
| Line Count | 1 |
| Word Count | 4 |
| Character Count | 32 |

This provides browser-level evidence of workflow creation, registered-tool execution, and result presentation.

## 📚 6. Demonstrated Knowledge Retrieval

The following knowledge-management operations were exercised:

- TXT document upload.
- Document indexing.
- Knowledge search.
- Retrieval of relevant information.
- Citation information.
- Analysis Agent interaction using knowledge sources.
- Report Agent generation using knowledge sources.

These checks demonstrated integration between the knowledge interface, backend RAG services, and supported AI functionality.

## 🧠 7. Demonstrated Agent Memory

The following memory operations were exercised:

- Memory creation.
- Memory listing.
- Memory inspection.
- Memory search.
- Memory editing.
- Memory deletion.
- Memory purge.

These checks demonstrated the memory-management interface and its corresponding operations.

## 🔌 8. Demonstrated Local AI Provider Integration

The Ollama provider was configured and successfully tested.

Previously demonstrated configuration:

| Setting | Value |
|---|---|
| Provider | Ollama |
| Runtime | `http://localhost:11434` |
| Chat Model | `qwen3.5:0.8b` |
| Embedding Model | `embeddinggemma:latest` |

The provider connectivity test succeeded during application validation.

## 📊 9. Analytics Verification

The observability and analytics API endpoints were accessed during frontend validation.

The tested areas included:

- Operational overview.
- Provider analytics.
- Agent analytics.
- Workflow analytics.
- Analytics interface rendering.

Some views displayed empty-state information because corresponding event data was not populated.

API accessibility and interface rendering should not be interpreted as proof that all analytics metrics were demonstrated with populated data.

## 🔐 10. Authentication Verification Status

The public registration database migration was successfully applied.

The following implementation capabilities are present:

- Public registration.
- Six-digit email OTP verification.
- Default operator-role assignment.
- Automatic sign-in after successful registration.
- Administrator bootstrap functionality.

A complete end-to-end SMTP registration journey should be marked as demonstrated only after successfully receiving an email, verifying the OTP, creating the account, and confirming automatic login.

## 📋 11. Feature Verification Matrix

The following matrix distinguishes implementation, automated verification, and browser demonstration.

| Feature | Implemented | Validation Evidence |
|---|---|---|
| Dashboard | Yes | Browser demonstrated |
| Visual Workflow Builder | Yes | Browser demonstrated |
| Workflow Execution | Yes | Automated tests and browser demonstration |
| Registered Tool Execution | Yes | Automated tests and browser demonstration |
| Knowledge Upload and Indexing | Yes | Automated tests and browser demonstration |
| Semantic Knowledge Search | Yes | Automated tests and browser demonstration |
| Analysis Agent | Yes | Browser demonstrated |
| Report Agent | Yes | Browser demonstrated |
| Persistent Agent Memory | Yes | Automated tests and browser demonstration |
| Ollama Provider | Yes | Provider connectivity demonstrated |
| Approval Management | Yes | Interface and backend implementation; complete lifecycle not yet demonstrated |
| Analytics | Yes | API and interface checks; some views displayed empty states |
| Public OTP Registration | Yes | Migration verified; full SMTP journey requires end-to-end confirmation |

## 📂 12. Evidence Directory

Verification screenshots can be maintained inside:

```text
docs/
└── evidence/
    ├── backend-tests.png
    ├── frontend-tests.png
    ├── frontend-build.png
    ├── workflow-execution.png
    ├── knowledge-search.png
    ├── ollama-provider-test.png
    └── database-migrations.png
```

Only include genuine terminal captures or application screenshots.

Do not use mock terminal outputs, fabricated test results, or generated images as proof of successful execution.

## 💡 Verification Philosophy

AgentOps-OS uses different forms of evidence for different engineering claims:

- **Implementation Evidence:** Source code and database migrations.
- **Automated Evidence:** Unit and integration test results.
- **Build Evidence:** Type checking and production-build output.
- **Demonstration Evidence:** Real application screenshots and successful execution.
- **Documentation Evidence:** Reproducible commands and configuration instructions.

**The objective is to make the project's capabilities independently inspectable and its verification claims reproducible.**

---

# 🖼️ Application Screenshots Gallery

This gallery presents the AgentOps-OS application through screenshots captured from its running development environment.

Each image highlights an individual application capability and provides a visual reference for the corresponding feature.

## 1. Application Overview

<p align="center">
  <img
    src="docs/screenshots/agentops-overview.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 2. Authentication and Login

<p align="center">
  <img
    src="docs/screenshots/register_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

<p align="center">
  <img
    src="docs/screenshots/login_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 3. Main Dashboard

<p align="center">
  <img
    src="docs/screenshots/Dashboard_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 4. Visual Workflow Builder

<p align="center">
  <img
    src="docs/screenshots/workflows_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 5. Workflow Execution

<p align="center">
  <img
    src="docs/screenshots/workflows_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 6. Analysis Agent

<p align="center">
  <img
    src="docs/screenshots/agents_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 7. Report Agent

<p align="center">
  <img
    src="docs/screenshots/agents_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 8. Knowledge Management

<p align="center">
  <img
    src="docs/screenshots/knowledge_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 9. Semantic Knowledge Search

<p align="center">
  <img
    src="docs/screenshots/knowledge_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 10. Persistent Agent Memory

<p align="center">
  <img
    src="docs/screenshots/agentops-overview.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 11. AI Provider Configuration

<p align="center">
  <img
    src="docs/screenshots/.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 12. Analytics and Observability

<p align="center">
  <img
    src="docs/screenshots/analytics_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 13. Human Approval Management

<p align="center">
  <img
    src="docs/screenshots/approvals_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>

## 14. User Registration

<p align="center">
  <img
    src="docs/screenshots/register_page.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>


---

# 🛡️ Security Practices

AgentOps-OS incorporates security controls across authentication, application authorization, database ownership, AI provider configuration, document processing, and workflow execution.

Security is treated as an application-wide engineering concern rather than a feature limited to the login page.

## 🔐 1. Password Security

The backend uses Argon2id for password hashing.

**Security practices:**
- Passwords are stored as Argon2id hashes.
- Plaintext passwords are not stored.
- Password length is validated.
- Stored password hashes can be checked for rehash requirements.
- Password verification errors are handled without exposing sensitive validation details.

The current password-length policy is between 12 and 128 characters.

## 🎫 2. JWT Authentication

AgentOps-OS uses signed JWT access tokens for authenticated application requests.

**Token validation includes:**
- Token signature verification.
- Expected issuer validation.
- Expiration validation.
- Required subject claim.
- Issued-at claim.
- Unique token identifier.

JWT tokens use the HS256 signing algorithm.

The configured signing secret must contain at least 32 characters.

Production configuration rejects unsafe development defaults.

## 👥 3. Role-Based Access Control

The application distinguishes between privileged and ordinary user roles.

**Account roles include:**

| Role | Purpose |
|---|---|
| Administrator | Privileged administrative operations |
| Operator | Standard application operations |
| Viewer | Restricted read-oriented tool access where permitted |

The backend performs authorization checks rather than relying exclusively on frontend visibility.

Public registration assigns the operator role automatically and does not allow visitors to select administrator privileges.

## 🔒 4. Owner-Scoped Data Access

User-owned resources are accessed through authenticated ownership context.

This applies to resources such as:

- Knowledge documents.
- Persistent memory records.
- AI provider configurations.
- Workflow-related application data.
- Approval-related operations.
- Observability information.

Authorization decisions are made on the backend.

A frontend component hiding a resource does not replace backend ownership checks.

## 🧾 5. Input and Output Validation

AgentOps-OS uses Pydantic schemas to validate API requests and structured application data.

The tool registry also defines input and output contracts for registered tools.

**Validation includes:**
- Request payload validation.
- Tool input-schema validation.
- Tool output-schema validation.
- Workflow definition validation.
- Task dependency validation.
- Unique task-key validation.
- Registered tool lookup.
- Role-based tool authorization.

This reduces the risk of malformed or unauthorized application operations.

## 🔌 6. AI Provider Credential Protection

AI provider configurations may contain sensitive credentials.

The platform encrypts hosted-provider API credentials before storing them in PostgreSQL.

**Security practices:**
- Keep encryption keys outside the repository.
- Never commit hosted-provider credentials.
- Avoid placing API keys in screenshots or logs.
- Restrict provider configuration operations to authorized users.
- Use environment-based secrets.

## 📧 7. Email OTP Security

The public registration flow uses six-digit email verification codes.

Authentication action tokens are stored as digests rather than raw token values.

The OTP-related configuration includes:
- OTP expiration.
- Maximum verification attempts.
- Resend cooldown.
- Request limits.
- OTP pepper configuration.

The registration flow assigns the default operator role after successful verification.

## 📂 8. Document Processing Security

Uploaded documents pass through document-validation and processing services.

**Implemented controls include:**
- Supported file-type validation.
- File-size limits.
- PDF page limits.
- Filename validation.
- Document ownership checks.
- Maximum chunk limits.
- Input validation before indexing.

Supported knowledge formats are PDF, TXT, and Markdown.

## ⚙️ 9. Workflow and Tool Execution Security

Registered tools contain trusted execution definitions.

Each tool specifies:
- Unique name.
- Input schema.
- Output schema.
- Handler function.
- Permitted user roles.
- Whether human approval is required.

The execution service checks registered tool authorization and validates payloads before execution.

Task handlers run in a separate child process with a configured hard timeout.

Approval requirements are obtained from trusted tool definitions rather than from arbitrary user-provided task data.

## 📊 10. Telemetry Privacy

The telemetry recorder is designed to collect operational metadata without retaining sensitive model content.

The telemetry API does not accept prompts, instructions, provider credentials, response bodies, or user content.

Telemetry persistence is best-effort: a telemetry storage failure must not cause an otherwise valid LLM request to fail.

## 🧾 11. Audit and Operational Records

AgentOps-OS maintains security-related audit records and execution information.

The audit-table protection uses database triggers to prevent ordinary UPDATE, DELETE, and TRUNCATE operations.

Workflow execution events and telemetry provide additional operational information.

## ⚠️ 12. Production Security Considerations

Before deploying AgentOps-OS to a production environment:

- Generate a strong, unique JWT secret.
- Configure SMTP securely.
- Generate and protect the OTP pepper.
- Configure the provider credential encryption key.
- Use strong database credentials.
- Restrict database network access.
- Use HTTPS.
- Configure trusted frontend origins.
- Protect backups and persistent volumes.
- Rotate credentials when necessary.
- Review application logs and audit information.
- Validate production environment settings before startup.

## 💡 Security Philosophy

AgentOps-OS applies security controls at multiple application boundaries.

**Authentication → Authorization → Validation → Ownership → Execution Controls → Secure Persistence**

The objective is to provide controlled access to AI capabilities, protect user-owned information, and reduce security risks throughout application execution.


---

# ⚡ Performance & Reliability

AgentOps-OS incorporates execution-management and error-handling mechanisms designed to improve the reliability of AI-powered application operations.

The platform focuses on controlled task execution, dependency management, bounded execution attempts, timeouts, structured error handling, persistent execution records, and operational visibility.

## 🔄 1. Dependency-Aware Execution

Workflow tasks are organized according to their declared dependencies.

The execution engine uses prerequisite-first topological ordering to determine task execution order.

**Reliability characteristics:**
- Dependency validation.
- Unknown dependency rejection.
- Duplicate dependency rejection.
- Self-dependency rejection.
- Circular dependency detection.
- Deterministic execution ordering.
- Skipping tasks whose prerequisites did not succeed.

This prevents workflows from attempting dependent tasks before their prerequisites have completed successfully.

## ⏱️ 2. Execution Timeouts

Registered workflow task handlers execute in separate child processes.

The task runner applies a configurable hard timeout to each execution.

**Execution controls:**
- Separate process execution.
- Configurable per-task timeout.
- Timeout detection.
- Process termination.
- Forced process termination when necessary.
- Structured error reporting.

The default task timeout is 300 seconds, and the configured timeout must be at least one second.

This prevents an individual registered task handler from running indefinitely within the workflow execution process.

## 🔁 3. Retry Management

Workflow tasks support configurable execution-attempt limits.

The task execution model includes:
- Maximum attempts.
- Current attempt count.
- Execution status.
- Error information.
- Execution timestamps.

The default maximum attempt count for a workflow task is three.

Retry behavior is managed by the workflow execution service and must respect the configured task policy.

Retries do not imply that every failed operation is automatically safe to repeat. Task handlers that interact with external systems must account for potential duplicate side effects.

## 🧪 4. Input and Output Contract Validation

Registered tools define Pydantic input and output models.

Before execution:
- The requested tool must be registered.
- The caller's role must be permitted.
- Input data is validated against the tool contract.

After execution:
- The handler result must have the expected structure.
- Output data is validated against the declared output model.
- Validation failures are reported as execution errors.

This creates a structured boundary between workflow definitions and executable application functionality.

## 🧑‍⚖️ 5. Approval-Based Execution Control

Some registered tools require human approval before execution.

The workflow execution service creates an approval request and pauses the workflow when a protected operation requires review.

After an eligible approval decision:
- The workflow can resume.
- Previously completed tasks are not repeated.
- The protected task can proceed through the execution service.
- Rejected or cancelled operations do not proceed as approved execution.

This provides a controlled execution path for operations requiring human oversight.

## 🗄️ 6. Persistent Execution State

Workflow and task execution information is stored in PostgreSQL.

Persistent records provide information about:
- Workflow status.
- Task status.
- Execution inputs.
- Execution outputs.
- Attempt counts.
- Error information.
- Task dependencies.
- Approval relationships.
- Execution events.

Persisted execution information helps developers inspect workflow activity and understand execution outcomes.

## 📡 7. Best-Effort Telemetry

Telemetry recording is deliberately designed not to interfere with the primary AI operation.

The telemetry recorder uses an independent short-lived database session.

If telemetry persistence fails, the failure is logged and the primary LLM request is allowed to continue.

This separates application execution reliability from optional observability persistence.

## 🛠️ 8. Error Handling

AgentOps-OS uses structured application errors and execution-state information to report failures.

Relevant failure categories include:
- Invalid workflow definitions.
- Unknown task dependencies.
- Circular dependency graphs.
- Unknown registered tools.
- Unauthorized tool execution.
- Invalid tool inputs.
- Invalid tool outputs.
- Handler execution errors.
- Execution timeout errors.
- Provider-related failures.
- Database and persistence errors.

## 📊 9. Reliability Mechanisms Summary

| Mechanism | Engineering Purpose |
|---|---|
| Dependency Ordering | Prevents execution before prerequisites |
| Cycle Detection | Rejects invalid workflow graphs |
| Retry Configuration | Bounds retry attempts |
| Hard Execution Timeout | Limits task-handler runtime |
| Child-Process Isolation | Separates registered task-handler execution |
| Input Validation | Rejects invalid tool payloads |
| Output Validation | Checks handler results |
| Role Authorization | Restricts tool execution |
| Human Approval | Adds controlled execution checkpoints |
| Persistent State | Maintains execution information |
| Best-Effort Telemetry | Prevents telemetry failure from breaking LLM generation |

## 📈 10. Performance Measurement and Optimization

The project includes operational telemetry and analytics capabilities that provide a foundation for inspecting execution behavior.

However, the existence of telemetry does not establish measured throughput, latency benchmarks, scalability limits, or production-load capacity.

Future performance evaluation can focus on:

- API response-time measurement.
- Workflow execution duration.
- Task-level execution timing.
- LLM provider response times.
- Embedding-generation latency.
- Vector retrieval performance.
- Database query performance.
- Frontend bundle-size optimization.
- Concurrent workflow execution behavior.

## ⚠️ 11. Current Performance Considerations

The frontend production build has previously completed successfully but reported a large JavaScript chunk warning.

This is a known optimization opportunity.

The application has not been presented as having completed formal load testing or production-scale performance benchmarking.

Actual performance depends on:
- Available hardware.
- Selected LLM provider.
- Local model size.
- Database resources.
- Document size and volume.
- Workflow complexity.
- Concurrent application activity.

## 💡 Reliability Philosophy

AgentOps-OS focuses on making application execution controlled, inspectable, and recoverable through explicit execution states and error-handling mechanisms.

**The engineering objective is not simply to execute AI tasks, but to establish clear boundaries around how tasks are validated, authorized, executed, monitored, and recorded.**

---

# ⚠️ Known Limitations

AgentOps-OS is an actively developed AI Agent Operations platform. Although its major backend and frontend capabilities have been implemented, some areas still have validation, deployment, or operational limitations.

The following points describe the current known limitations of the project.

## 1. Production Deployment

The current repository provides a local development environment using Docker Compose for PostgreSQL infrastructure.

**Current limitations:**
- Docker Compose does not currently deploy the complete frontend and backend application.
- Backend and frontend services are started independently during local development.
- A complete production deployment configuration has not yet been established.
- Production infrastructure, monitoring, and scaling have not been validated.

## 2. Live Agent Inventory

The dashboard provides information about workflow activity and agent-related operations.

However, the current backend does not expose a dedicated live running-agent inventory API.

Consequently:
- The dashboard displays the agent inventory as unavailable when it cannot obtain that information.
- Running workflow tasks should not automatically be interpreted as independently running agents.
- Agent-related analytics depend on the telemetry information available to the backend.

## 3. Analytics Data Availability

The observability infrastructure and analytics APIs are implemented.

However, the information displayed depends on the operational events and telemetry records available for the authenticated account.

**Current limitations:**
- Some analytics views may display empty states when corresponding records are unavailable.
- Token totals and cost information should not be presented as validated aggregate billing metrics without supporting provider data.
- Agent performance metrics depend on agent-attributed telemetry.
- Analytics completeness depends on the events recorded by the application.

## 4. Human Approval Validation

The backend includes approval-related services, APIs, and workflow execution controls.

The application has also demonstrated the approval-management interface and its empty state.

However, the complete browser-level lifecycle still requires additional end-to-end validation:

1. Create a workflow task requiring approval.
2. Execute the workflow.
3. Confirm that execution pauses for approval.
4. Review the approval request.
5. Submit an approval or rejection decision.
6. Verify the resulting workflow behavior.

The implementation of approval functionality should therefore be distinguished from a fully demonstrated end-to-end approval scenario.

## 5. Email OTP Registration

Public self-service registration and six-digit email OTP verification have been implemented.

The database migration for public registration verification has been successfully applied.

The complete registration flow still requires validation against a working SMTP environment, including:

- Email delivery.
- OTP expiration.
- OTP verification.
- Account creation.
- Default operator-role assignment.
- Automatic sign-in.

SMTP-dependent behavior requires valid email configuration.

## 6. Performance Benchmarking

The project includes execution timeouts, configurable retries, task execution controls, and telemetry.

However, formal performance benchmarking has not been completed.

The following have not been established as production performance guarantees:

- Maximum concurrent workflow executions.
- Maximum supported users.
- API throughput.
- Large-document indexing throughput.
- Vector-search performance under heavy load.
- Large-scale LLM execution performance.

## 7. Frontend Bundle Size

The frontend production build completes successfully.

However, Vite has reported a large JavaScript chunk warning after minification.

This is a known optimization opportunity for future development.

## 8. AI Provider Dependencies

Local model execution through Ollama provides an alternative to hosted model APIs.

However:
- Model performance depends on available hardware.
- Local inference can be slower on resource-constrained machines.
- Hosted providers require their own credentials and configuration.
- Provider availability depends on the configured runtime and external service.

## 9. Cross-Platform Validation

The primary development and verification environment used for this project is Windows with PowerShell.

Equivalent Linux and macOS development instructions have not been comprehensively validated across all supported environments.

## 10. Screenshot and Demonstration Data

Some README interface images may contain illustrative sample data to demonstrate populated dashboard states.

These images are visual representations of the application interface, not proof that the displayed records exist in the live database.

Actual implementation evidence should be provided through genuine application captures, automated test results, and reproducible execution records.

---

### 📌 Transparency Statement

AgentOps-OS is a substantial full-stack AI engineering project, but implementation does not automatically imply production readiness.

Known limitations are documented to distinguish implemented capabilities, automated verification, browser demonstrations, and areas requiring further validation.

---

# 🚀 Future Enhancements

AgentOps-OS provides a foundation for managing AI-powered workflows and agent operations.

Future development can extend the platform with improved execution capabilities, evaluation infrastructure, operational monitoring, deployment automation, and enterprise-oriented administration.

The following items represent potential improvements beyond the currently implemented functionality.

## 1. Advanced Multi-Agent Collaboration

Extend the existing specialized-agent architecture with more advanced coordination capabilities.

**Potential Improvements:**
- More specialized agent implementations.
- Explicit agent-to-agent handoff.
- Shared execution context.
- Advanced coordination strategies.
- Agent collaboration visualization.
- Improved orchestration observability.

## 2. Advanced Agent Evaluation

Expand the evaluation infrastructure to assess agent behavior and output quality.

**Potential Improvements:**
- Expanded agent-output quality benchmarks.
- Retrieval-quality evaluation.
- Response relevance scoring.
- Groundedness and citation evaluation.
- Multi-agent execution evaluation.
- Historical evaluation comparisons.
- Evaluation dataset management.

## 3. Advanced Workflow Capabilities

Extend the workflow engine and visual builder.

**Potential Improvements:**
- More advanced conditional branching.
- Parallel task execution.
- Workflow scheduling.
- More execution-control options.
- Workflow templates.
- Reusable workflow components.
- Improved execution visualization.

## 4. Advanced Observability

Extend the current telemetry and analytics architecture.

**Potential Improvements:**
- More detailed agent execution tracing.
- Improved token and cost aggregation.
- Provider latency comparisons.
- Workflow performance dashboards.
- Custom reporting.
- Alerting and notification mechanisms.
- Exportable operational reports.

## 5. Production Deployment

Establish a complete deployment architecture.

**Potential Improvements:**
- Containerized backend deployment.
- Production frontend hosting.
- Reverse proxy configuration.
- HTTPS and TLS termination.
- Production database management.
- Automated backups.
- CI/CD pipelines.
- Deployment health monitoring.

## 6. Performance and Scalability

Improve the application's ability to handle larger workloads.

**Potential Improvements:**
- Formal load testing.
- Concurrent workflow execution.
- Background job processing.
- Caching improvements.
- Database query optimization.
- Large-document processing improvements.
- Frontend code splitting.
- Performance benchmarking.

## 7. Enterprise Administration

Extend the existing authentication and administration functionality.

**Potential Improvements:**
- More granular permission policies.
- Advanced user and role administration.
- Workspace-level configuration.
- Multi-workspace support.
- Advanced audit-log exploration.
- Administrative reporting.
- Configurable approval policies.

## 8. Knowledge Management Improvements

Extend the RAG subsystem.

**Potential Improvements:**
- Additional document formats.
- Advanced retrieval strategies.
- Hybrid keyword and vector search.
- Re-ranking models.
- Knowledge collection management.
- Retrieval evaluation.
- Improved citation visualization.
- Knowledge-source synchronization.

## 9. Memory Improvements

Expand persistent memory management.

**Potential Improvements:**
- Advanced memory consolidation.
- Memory deduplication.
- Improved relevance ranking.
- Memory lifecycle policies.
- Memory evaluation.
- Better memory visualization.
- More advanced agent-specific memory strategies.

## 10. Developer Experience

Improve the experience of extending and integrating AgentOps-OS.

**Potential Improvements:**
- Developer SDK.
- More reusable integration interfaces.
- Plugin architecture.
- Expanded API examples.
- Automated documentation generation.
- Additional integration tests.
- CI-based quality checks.

---

### 🌟 Long-Term Vision

The long-term vision is to evolve AgentOps-OS into a more comprehensive operations environment for AI-powered applications.

The focus is on improving:

**Agent Collaboration → Workflow Intelligence → Evaluation → Security → Observability → Scalability**

These enhancements are proposals and should not be interpreted as currently completed features.

---

# 🛠️ Troubleshooting

This section covers common installation, configuration, database, backend, frontend, and AI provider issues encountered while running AgentOps-OS locally.

## 1. Docker Command Not Recognized

**Problem:**

```text
docker : The term 'docker' is not recognized
```

**Possible Causes:**
- Docker Desktop is not installed.
- Docker Desktop is not running.
- Docker is not available in the system PATH.

**Resolution:**

1. Install Docker Desktop.
2. Start Docker Desktop.
3. Open a new PowerShell terminal.
4. Verify the installation.

```powershell
docker --version

docker compose version
```

## 2. PostgreSQL Port Already in Use

**Problem:**

```text
Ports are not available
```

This can happen when another PostgreSQL service already occupies port `5432`.

**Resolution:**

Change the host port in the root `.env` file.

```env
POSTGRES_PORT=5433
```

Make sure the database URLs use the same host port.

```env
DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops

TEST_DATABASE_URL=postgresql+psycopg://agentops:agentops@localhost:5433/agentops_test
```

Restart the database service:

```powershell
docker compose up -d --wait db
```

## 3. PostgreSQL Container Is Not Healthy

**Problem:**

The database container starts but does not reach a healthy state.

**Inspect the container:**

```powershell
docker compose ps
```

**Inspect database logs:**

```powershell
docker compose logs db
```

**Restart the database service:**

```powershell
docker compose restart db
```

Check that the `.env` credentials and database configuration are consistent.

## 4. Backend Dependency Installation Fails

**Problem:**

Python packages are not installed correctly.

**Resolution:**

Navigate to the backend directory.

```powershell
cd backend
```

Verify Python:

```powershell
uv python list
```

Install dependencies:

```powershell
uv sync --extra dev
```

Verify the Python environment:

```powershell
uv run python --version
```

## 5. Database Connection Error

**Problem:**

```text
Connection refused
```

**Possible Causes:**
- PostgreSQL is not running.
- The host port is incorrect.
- Database credentials do not match.
- The database URL is incorrect.

**Resolution:**

Check Docker Compose:

```powershell
docker compose ps
```

Check the database logs:

```powershell
docker compose logs db
```

Verify that `DATABASE_URL` uses the correct host port and credentials.

## 6. Alembic Migration Failure

**Problem:**

Database migrations fail during startup or development.

**Resolution:**

From the backend directory:

```powershell
uv run alembic current
```

Inspect migration history:

```powershell
uv run alembic history
```

Check the current database URL and confirm that the intended development database is being used.

Apply migrations:

```powershell
uv run alembic upgrade head
```

Do not manually modify Alembic version records to bypass migration failures.

## 7. Uvicorn Command Not Recognized

**Problem:**

```text
uvicorn is not recognized
```

**Resolution:**

Run Uvicorn through the managed Python environment:

```powershell
uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000
```

## 8. Frontend Vite Command Not Recognized

**Problem:**

```text
'vite' is not recognized as an internal or external command
```

**Resolution:**

Navigate to the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm ci
```

Start the frontend:

```powershell
npm run dev
```

## 9. Frontend Cannot Connect to Backend

**Problem:**

The frontend loads, but API requests fail.

**Check the backend:**

```text
http://127.0.0.1:8000/api/v1/health/ready
```

**Check the frontend:**

```text
http://127.0.0.1:5173
```

Verify the Vite proxy target:

```env
VITE_BACKEND_PROXY_TARGET=http://127.0.0.1:8000
```

Restart the frontend after changing its environment configuration.

## 10. Ollama Connection Error

**Problem:**

The application cannot connect to the local model runtime.

**Check Ollama:**

```powershell
ollama --version

Invoke-RestMethod http://localhost:11434/api/tags
```

Check installed models:

```powershell
ollama list
```

Download missing models:

```powershell
ollama pull qwen3.5:0.8b

ollama pull embeddinggemma
```

Verify:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen3.5:0.8b
OLLAMA_EMBEDDING_MODEL=embeddinggemma
```

Restart the backend after changing configuration.

## 11. Knowledge Indexing Fails

**Possible Causes:**
- Ollama is not running.
- The embedding model is unavailable.
- The embedding dimensions do not match the database schema.
- The document exceeds configured processing limits.
- The file format is unsupported.

**Resolution:**

Verify the embedding model:

```powershell
ollama list
```

Test Ollama connectivity:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Supported document formats include:

- PDF
- TXT
- Markdown

Review the backend logs for document-processing or embedding errors.

## 12. Email OTP Is Not Received

**Possible Causes:**
- Incorrect SMTP host or port.
- Invalid SMTP credentials.
- Sender address is not configured.
- STARTTLS configuration is incorrect.
- Email provider security restrictions.

**Resolution:**

Verify the SMTP settings in the root `.env` file.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-smtp-app-password
SMTP_FROM_EMAIL=your-email@example.com
SMTP_STARTTLS=true
```

Use valid credentials for your email provider.

Never expose SMTP passwords or OTP secrets in logs or screenshots.

## 13. Integration Tests Fail

**Possible Causes:**
- Test database is unavailable.
- `TEST_DATABASE_URL` points to an incorrect database.
- The database name does not satisfy the test-database safety requirements.
- Database migrations have not been applied to the test database.

**Resolution:**

Check the integration-test database configuration.

```powershell
$env:AGENTOPS_REQUIRE_DB = "1"

uv run pytest -m integration
```

Do not point integration tests at your ordinary development database.

## 14. Frontend Build Reports Large Chunk Warnings

**Problem:**

Vite reports that some JavaScript chunks exceed the recommended size.

The build may still complete successfully.

**Resolution:**

Review:
- Large frontend dependencies.
- Code-splitting opportunities.
- Lazy-loaded routes.
- Dynamic imports.
- Unnecessary bundled modules.

This is a frontend optimization issue, not necessarily a failed production build.

## 15. VS Code Markdown Preview Does Not Display Images

**Possible Causes:**
- Incorrect relative image path.
- Image is stored in another folder.
- Incorrect filename extension.
- Backslashes have been added before HTML tags.
- Markdown image syntax is malformed.

**Correct example:**

```html
<p align="center">
  <img
    src="docs/screenshots/agentops-overview.png"
    alt="AgentOps-OS Application Overview"
    width="100%"
  >
</p>
```

Use paths relative to the root `README.md`.

---

### 💡 Still Experiencing an Issue?

Check the application logs, verify environment configuration, and reproduce the issue using the documented setup commands.

When reporting an issue, include:
- Error message.
- Relevant terminal output.
- Steps to reproduce.
- Operating system and software versions.
- Relevant application logs with secrets removed.

Report reproducible issues through the repository's GitHub Issues section.

---

# 🤝 Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

AgentOps-OS is an actively developed full-stack AI application project. Contributions that improve functionality, reliability, security, documentation, and developer experience are valuable.

## 🌱 1. Ways to Contribute

You can contribute in several ways:

- Report bugs.
- Suggest new features.
- Improve existing functionality.
- Optimize backend services.
- Improve frontend components.
- Enhance workflow orchestration.
- Improve knowledge retrieval.
- Add automated tests.
- Improve security and validation.
- Update documentation.
- Improve installation and development instructions.

## 📥 2. Fork the Repository

Start by forking the project on GitHub.

Repository:

https://github.com/vivekgadhe/AgentOps-OS

Clone your fork:

```powershell
git clone https://github.com/YOUR_USERNAME/AgentOps-OS.git

cd AgentOps-OS
```

Add the original repository as the upstream remote:

```powershell
git remote add upstream https://github.com/vivekgadhe/AgentOps-OS.git
```

## 🌿 3. Create a Feature Branch

Create a separate branch for your contribution.

```powershell
git checkout -b feature/your-feature-name
```

For bug fixes:

```powershell
git checkout -b fix/your-bug-name
```

## 💻 4. Follow Project Development Practices

Please follow these practices:

- Maintain the existing project architecture.
- Use clear and descriptive names.
- Keep backend services modular.
- Use Pydantic schemas for API contracts.
- Follow existing frontend component conventions.
- Add tests for new functionality.
- Avoid committing generated files.
- Keep credentials and secrets out of source control.

## 🧪 5. Run Tests Before Submitting

### Backend

```powershell
cd backend

uv sync --extra dev

uv run pytest

uv run ruff check src tests

uv run ruff format --check src tests

uv run mypy src
```

### Frontend

```powershell
cd frontend

npm ci

npm run check
```

Resolve relevant failures before submitting your changes.

## 📝 6. Commit Your Changes

Use descriptive commit messages.

Example:

```powershell
git add .

git commit -m "Add improved workflow execution handling"
```

Other examples:

```text
Fix knowledge retrieval validation

Improve provider configuration handling

Add memory management tests

Update installation documentation
```

## 📤 7. Submit a Pull Request

Push your feature branch:

```powershell
git push origin feature/your-feature-name
```

Open a Pull Request against the original repository's `main` branch.

Include:
- A clear description.
- The problem being addressed.
- Implementation details.
- Relevant test results.
- Screenshots for interface changes.
- Any configuration or migration requirements.

## 🔍 8. Contribution Guidelines

Contributions should:

- Have a clear purpose.
- Avoid unrelated modifications.
- Include relevant validation.
- Preserve existing working functionality.
- Avoid introducing unnecessary dependencies.
- Follow the existing coding and formatting conventions.
- Document changes that affect setup or configuration.

For larger architectural changes, open an issue for discussion before beginning implementation.

## 💜 Thank You

Every useful contribution helps improve AgentOps-OS.

Whether you report a bug, improve documentation, contribute a feature, or suggest an architectural improvement, your involvement is appreciated.

---

# 🙏 Acknowledgements

AgentOps-OS is built using modern open-source frameworks, libraries, development tools, and AI technologies.

We acknowledge the developers and communities behind these projects for providing the tools and resources that make modern AI application development possible.

## ⚙️ Backend Technologies

| Project | Contribution | Official Website |
|---|---|---|
| Python | Backend programming language | https://www.python.org/ |
| FastAPI | Backend REST API framework | https://fastapi.tiangolo.com/ |
| Pydantic | Data validation and settings | https://docs.pydantic.dev/ |
| SQLAlchemy | Database ORM | https://www.sqlalchemy.org/ |
| Alembic | Database schema migrations | https://alembic.sqlalchemy.org/ |
| Uvicorn | ASGI application server | https://www.uvicorn.org/ |

## 🎨 Frontend Technologies

| Project | Contribution | Official Website |
|---|---|---|
| React | Frontend interface development | https://react.dev/ |
| TypeScript | Static type checking | https://www.typescriptlang.org/ |
| Vite | Development and production build tooling | https://vite.dev/ |
| Tailwind CSS | Interface styling | https://tailwindcss.com/ |
| React Router | Frontend routing | https://reactrouter.com/ |
| TanStack Query | Server-state management | https://tanstack.com/query |
| Recharts | Data visualization | https://recharts.org/ |
| Lucide | Interface icons | https://lucide.dev/ |

## 🗄️ Database and Retrieval Technologies

| Project | Contribution | Official Website |
|---|---|---|
| PostgreSQL | Relational database | https://www.postgresql.org/ |
| pgvector | Vector similarity search | https://github.com/pgvector/pgvector |
| Psycopg | PostgreSQL Python driver | https://www.psycopg.org/ |
| pypdf | PDF text extraction | https://pypdf.readthedocs.io/ |

## 🤖 AI and Local Model Ecosystem

| Project | Contribution | Official Website |
|---|---|---|
| Ollama | Local LLM and embedding runtime | https://ollama.com/ |
| Qwen | Language-model family | https://github.com/QwenLM |
| EmbeddingGemma | Local embedding model | https://ai.google.dev/gemma |

## 🧪 Testing and Development Tools

| Project | Contribution | Official Website |
|---|---|---|
| pytest | Backend testing | https://pytest.org/ |
| Vitest | Frontend testing | https://vitest.dev/ |
| Ruff | Python linting and formatting | https://docs.astral.sh/ruff/ |
| mypy | Python static type checking | https://mypy-lang.org/ |
| Docker | Containerized infrastructure | https://www.docker.com/ |
| uv | Python package and environment management | https://docs.astral.sh/uv/ |
| Git | Version control | https://git-scm.com/ |
| GitHub | Source-code hosting and collaboration | https://github.com/ |

## 🌍 Open-Source Community

We appreciate the open-source developers, maintainers, researchers, and communities who continuously improve the tools and technologies used in this project.

Their work makes it possible to experiment with modern software architectures, AI integrations, vector retrieval, and full-stack development.

## 💜 Special Appreciation

A special thank-you to the maintainers of the libraries, frameworks, model projects, and development tools integrated into AgentOps-OS.

**Built with open-source technologies and a commitment to practical AI engineering.**

---

## 👨‍💻 Developer

### Building practical software with Python, Full-Stack Development and AI Engineering.

AgentOps-OS is a hands-on engineering project focused on exploring how modern AI capabilities can be integrated into a complete, maintainable software platform.

My interests include Python backend development, full-stack application engineering, Large Language Models, AI agents, workflow orchestration, and Retrieval-Augmented Generation.

Through AgentOps-OS, I have explored the practical integration of AI engineering concepts with backend architecture, frontend development, database systems, authentication, automated testing, and operational observability.

### Technical Interests

- Python Backend Development
- FastAPI and REST API Design
- React and TypeScript
- AI Agents and LLM Applications
- Retrieval-Augmented Generation (RAG)
- Workflow Orchestration
- PostgreSQL and Vector Databases
- Docker and Application Infrastructure
- Software Testing and Code Quality

### Connect with the Developer

<p align="center">
  <a href="https://github.com/vivekgadhe">
    <img src="https://img.shields.io/badge/GitHub-View%20Profile-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile">
  </a>
  &nbsp;
  <a href="YOUR_LINKEDIN_PROFILE_URL">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Profile">
  </a>
</p>

<p align="center">
  <strong>Interested in Python Development, AI Engineering and building intelligent applications.</strong>
</p>

---

## 💬 Support & License

### 🛠️ Support

Need help with AgentOps-OS, found a bug, or have an idea for improving the platform?

You can use the GitHub repository to report issues and share suggestions.

**Available Support Channels:**

<p align="center">
  <a href="https://github.com/vivekgadhe/AgentOps-OS/issues">
    <img src="https://img.shields.io/badge/GitHub-Report%20an%20Issue-181717?style=for-the-badge&logo=github&logoColor=white" alt="Report an Issue">
  </a>
  &nbsp;
  <a href="https://github.com/vivekgadhe/AgentOps-OS">
    <img src="https://img.shields.io/badge/GitHub-Project%20Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="Project Repository">
  </a>
</p>

When reporting an issue, include:

- A clear description of the problem.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Relevant error messages or logs.
- Environment and software versions.
- Screenshots, when relevant.

Please remove passwords, API keys, access tokens, and other sensitive information before sharing logs.

### 💡 Feature Requests

Suggestions for improving AgentOps-OS are welcome.

Feature requests can include:

- New AI agent capabilities.
- Workflow orchestration improvements.
- Knowledge retrieval enhancements.
- Additional AI provider integrations.
- Security and reliability improvements.
- Analytics and observability enhancements.
- Frontend and developer-experience improvements.

### 📄 License

The licensing terms for AgentOps-OS should be defined through a license file in the root directory of the repository.

Until a license is selected and added, the project should not be described as MIT-licensed or as granting unrestricted permission to reuse its source code.

**License:** To be confirmed.

### 🌟 Project Repository

<p align="center">
  <a href="https://github.com/vivekgadhe/AgentOps-OS">
    <strong>AgentOps-OS on GitHub</strong>
  </a>
</p>

<p align="center">
  Built with Python, React, TypeScript, PostgreSQL and AI technologies.
</p>

<p align="center">
  <strong>Build. Orchestrate. Evaluate. Observe.</strong>
</p>

---
