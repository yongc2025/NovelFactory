from novel_factory.db.connection import get_connection

def fix_current():
    pid = "20260601_172217_9a0afb"
    title = "主角身份：一个赛博朋克世界的资深美食厨师"
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO projects (id, title) VALUES (?, ?)",
            (pid, title)
        )
    print(f"Fixed project {pid}")

if __name__ == "__main__":
    fix_current()
