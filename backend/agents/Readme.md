---

title: Aegis Agents API Tutorial
description: Learn how to use the Aegis Agents API to run Autogen agents in production.
---------------------------------------------------------------------------------------

## Introduction

Aegis leverages **Autogen agents** to automate complex workflows using AI-driven decision-making. The **Aegis Agents API** provides a structured way to deploy and execute these agents in a production environment.

### Key Concepts

- **Tasks**: Define what needs to be accomplished.
- **Teams**: A logical grouping of agents that collaborate on a task (based on Autogen Teams).
- **Sessions**: A container for runs that provides contextual continuity by linking tasks with teams.
- **Runs**: Individual executions of an Autogen Team to solve a task within a session.

This tutorial will guide you through setting up an **Automarking Task**, configuring a **Team**, starting a **Session**, and executing a **Run** using the Aegis API. Automarking is just an example; the API is capable of running various AI-driven workflows.

---

## Step 1: Create a Task

To create an **Automarking Task**, send the following request:

```http
POST /api/v1/task
```

```json
{
  "name": "Automarking Task",
  "description": "Evaluate student responses for correctness.",
  "version": "1.0.0",
  "created_by_user_id": "<user_id>"
}
```

### Response:

```json
{
  "message": "Task created.",
  "data": {
    "id": "<task_id>",
    "name": "Automarking Task",
    "description": "Evaluate student responses for correctness."
  }
}
```

---

## Step 2: Create a Team

A **Team** consists of one or more agents that collaborate to complete a task. Below is an example of a **Automarking Assistant** agent:

```http
POST /api/v1/team
```

```json
{
  "component": {
    "provider": "autogen_agentchat.agents.AssistantAgent",
    "component_type": "agent",
    "version": 1,
    "component_version": 1,
    "description": "An agent that evaluates student responses based on predefined grading criteria.",
    "label": "Automarking Assistant",
    "config": {
      "name": "automarking_agent",
      "model_client": {
        "provider": "autogen_ext.models.openai.OpenAIChatCompletionClient",
        "component_type": "model",
        "version": 1,
        "component_version": 1,
        "description": "Chat completion client for OpenAI hosted models.",
        "label": "OpenAIChatCompletionClient",
        "config": {
          "model": "gpt-4o-mini"
        }
      },
      "description": "An agent that evaluates student responses for correctness and provides grading feedback.",
      "system_message": "You are an AI grader. Your task is to evaluate student responses based on the provided grading rubric. Provide structured feedback including reasoning, a binary satisfactory flag, and scores for relevance and completeness. Respond in JSON format.",
      "model_client_stream": false
    }
  }
}
```

### Response:

```json
{
  "message": "Team created.",
  "data": {
    "id": "<team_id>",
    "component": <team_component>
  }
}
```

---

## Step 3: Create a Session

A **Session** groups multiple runs of a task and ensures continuity. Create a session linked to the **Automarking Task** and **Team**:

```http
POST /api/v1/session
```

```json
{
  "task_id": "<task_id>",
  "team_id": "<team_id>",
  "created_by_user_id": "<user_id>",
  "archived": false,
  "team_metadata": {}
}
```

### Response:

```json
{
  "message": "Session created.",
  "data": {
    "id": "<session_id>",
    "task_id": "<task_id>",
    "team_id": "<team_id>"
  }
}
```

---

## Step 4: Create a Run

A **Run** represents a single execution of a task within a session. Here’s how to start an **Automarking Run**:

```http
POST /api/v1/run
```

```json
{
  "session_id": "<session_id>",
  "task_id": "<task_id>",
  "run_task": {
    "source": "string",
    "content": {
      "question": "Name 3 capital cities in Australia.",
      "model_answer": "Canberra, Sydney, ...",
      "student_answer": "Canberra,..."
    },
    "message_type": "dict"
  },
  "batch_mode": false,
  "created_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "archived": false
}
```

### Response:

```json
{
  "message": "Run created.",
  "meta": {},
  "data": {
    "session_id": "<session_id>",
    "task_id": "<task_id>",
    "run_task": {
      "source": "string",
      "content": {
        "question": "A",
        "model_answer": "B"
      },
      "message_type": "dict"
    },
    "batch_mode": false,
    "created_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "archived": false,
    "id": "<run_id>",
    "messages": []
  }
}
```

---

## Step 5: Retrieve Results

You can retrieve all runs within a session:

```http
GET /api/v1/run
```

```http
GET /api/v1/run/<run_id>
```

### Example Response:

```json
{
  "message": "Data got correctly",
  "meta": {},
  "data": {
    "session_id": "0195c641-0d8e-7061-a65b-79051d4929ca",
    "task_id": "0195c63e-e1ca-7751-9721-84b4b8d310ee",
    "run_task": {
      "source": "string",
      "content": {
        "question": "A",
        "model_answer": "B"
      },
      "message_type": "dict"
    },
    "batch_mode": false,
    "created_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "archived": false,
    "id": "0195c6b9-5c97-796b-aa06-2a267d7d328e",
    "status": "complete",
    "team_result": {
      "task_result": {
        "messages": [
          {
            "source": "automarking_agent",
            "content": {
              "reasoning": "The student correctly identified Canberra, Sydney and Melbourne.",
              "satisfactory": true,
              "relevance_score": 10,
              "completeness_score": 10,
              "confidence_score": 0.9
            },
            "type": "dict"
          }
        ],
        "stop_reason": null
      }
    },
    "error_message": null,
    "created_at": "2025-03-24T05:56:31.511798Z",
    "estimated_completion_time": null
  }
}
```

---

## Error Testing with Stub Sequences

The Aegis Agents API supports **simulated error testing** via a special stub model: `stub_error_sequence`. This model is designed to sequentially raise errors from LiteLLM’s supported exception types, enabling robust error handling and observability testing in your application.

### Supported Errors

A predefined sequence includes the full set of LiteLLM exception types. Refer to the official docs for details:

🔗 [LiteLLM Exception Mapping Documentation](https://docs.litellm.ai/docs/exception_mapping)

### Simulate Errors Using Agent Runs

#### 1. Create a Session with the `stub_error_sequence` Model

To simulate errors, create a session using `team_metadata.model = "stub_error_sequence"`.

```json
POST /api/v1/session
```

```json
{
  "task_id": "<task_id>",
  "team_id": "<team_id>",
  "created_by_user_id": "<user_id>",
  "archived": false,
  "team_metadata": {
    "model": "stub_error_sequence"
  }
}
```

#### 2. Create Runs to Trigger Each Error in the Sequence

Each time you create a run, the stub model will raise the next error from the sequence. So you are able to cycle through all the error messages you will see.

```json
POST /api/v1/run
```

```json
{
  "session_id": "<session_id>",
  "task_id": "<task_id>",
  "run_task": {
    "source": "test",
    "content": {
      "question": "trigger error"
    },
    "message_type": "dict"
  },
  "created_by_user_id": "<user_id>"
}
```

The error will be logged in the run’s metadata:

```json
{
  "status": "error",
  "error_message": "litellm.RateLimitError: You've hit the rate limit",
  "error_details": {
    "type": "RateLimitError",
    "message": "...",
    "status_code": 429,
    "llm_provider": "openai",
    "model": "stub_error_sequence"
  }
}
```

Use this feature to test how your system handles retries, logs errors, and populates dashboards.

---

## Conclusion

This tutorial demonstrated how to:

- Create a **Task**
- Configure a **Team**
- Start a **Session**
- Execute a **Run**
- Retrieve Results
- Test Error Handling with Stub Sequences

With the Aegis Agents API, you can build **scalable, production-ready AI workflows** using **Autogen Agents**.
