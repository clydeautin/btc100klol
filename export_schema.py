from app import db  # Replace 'your_app' with your actual Flask app package/module name

# Export the schema
with open("schema.sql", "w") as f:
    for line in db.engine.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'").fetchall():
        f.write(f"{line}\n")