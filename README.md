# cf-migration

## Project Structure
```
neo_cf_migrator/
│── graph.py              # LangGraph workflow
│── nodes/
│    ├── planner.py       # Decides what to migrate
│    ├── transformer.py   # Applies changes (Neo → CF)
│    └── writer.py        # Writes new folder/files
│── utils/
│    └── file_ops.py      # File system helpers
│── main.py               # Entry point to run migration
```

## Info
- This uses the OpenAI model via LangChain. You must set OPENAI_API_KEY in your environment before running.
- The code is written to be practical and robust, but LLM outputs vary; always review generated manifests/files before pushing to production.
- This is an automated migration assistant. It will try to transform configs (neo-app.json, xs-app.json, mta.yaml, etc.) into a CF-friendly manifest.yml and update references, but manual review is required.