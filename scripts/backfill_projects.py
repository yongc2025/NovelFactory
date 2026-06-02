import json
from pathlib import Path
from novel_factory.db.connection import get_connection

def backfill():
    data_dir = Path("data")
    projects_json = data_dir / "projects.json"
    if not projects_json.exists():
        print("No projects.json found.")
        return

    with open(projects_json, "r", encoding="utf-8") as f:
        index = json.load(f)

    with get_connection() as conn:
        for pid in index:
            print(f"Backfilling {pid}...")
            project_file = data_dir / pid / "project.json"
            if not project_file.exists():
                print(f"  Warning: {project_file} not found.")
                continue
            
            with open(project_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            
            conn.execute(
                """
                INSERT INTO projects (id, title, premise, genre, target_words, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (
                    pid, meta.get("title"), meta.get("inspiration") or meta.get("premise"), 
                    meta.get("genre"), meta.get("target_words"), meta.get("status"), 
                    meta.get("created_at"), meta.get("updated_at")
                )
            )
    print("Done.")

if __name__ == "__main__":
    backfill()
