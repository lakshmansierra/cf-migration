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
