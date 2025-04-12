# Data Analyst Agent in LangGraph + Open WebUI

> This repo contains code demos that were discussed in ["Open WebUI + LangGraph AI Agents with Python Executor and Postgres Database-A Walkthrough"](https://www.youtube.com/live/4fg0KGmSjv8?si=iWemebZ8Xlkd1vkx&utm_source=github&utm_medium=github-readme).

**Disclaimer:** This repository is just a demonstration of what is possible with LangGraph agents and Open WebUI integration. It will not be actively maintained.

This repo will teach you how to:
- Create AI Agent (agent AI) in LangGraph that can use Python Executor and Postgres Database
- Integrate the LangGraph agents with Open WebUI via Pipelines

> Note that we use OpenAI API models for fast prototyping. You can use Ollama to run local LLM API. However, the instruction is not provided in this repo.

## Set Up
1. Create conda environment with python=3.12.9
2. Install dependencies with poetry
```shell
poetry install
```
3. Set up OpenAI API key via `.env` file (which should be located in `langgraph_agents/config/`):
```shell
OPENAI_API_KEY=your_openai_api_key
```
4. Set up Postgres connection string in `.env` file (which should be located in `langgraph_agents/config/`). This is optional if you do not want to access Postgres database.
```shell
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
POSTGRES_DB=your_postgres_db
```

## Run
1. Activate your conda environment
2. Simply run:
```shell
sh start.sh
```
3. Open Open WebUI and make sure your pipeline is connected to it.
4. Use 'Data Analyst' agent as a model to chat.

## Sharing & Crediting

> Feel free to copy and distribute, but we appreciate you giving us credits.

## ⛓️Connect with Us:

👍 Like | 🔗 Share | 📢 Subscribe | 💬 Comments | ❓ Questions

[LinkedIn](www.linkedin.com/company/casedonebyai) <br>
[YouTube](www.youtube.com/@CaseDonebyAI) <br>
[Facebook](www.facebook.com/casedonebyai) <br>
[TikTok](www.tiktok.com/@casedonebyai) <br>
[Github](www.github.com/casedone) <br>
[SubStack](casedonebyai.substack.com)