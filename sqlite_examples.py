import sqlite3
import json

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('/databases/papers_sqlite/papers.db')
cursor = conn.cursor()

# Create a table to store your JSON objects
cursor.execute('''
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    data JSON
)
''')

def write_progress(index: int):
    with open('progress.txt', 'w') as f:
        f.write(str(index))

def load_progress() -> int:
    with open('progress.txt', 'r') as f:
        return int(f.read())

# Assume 'papers' is a list of dictionaries, each representing a JSON object
try:
    for index, paper in enumerate(papers):
        print(f'Processing paper {index+1} of {len(papers)}')
        # Convert the dictionary to a JSON string
        json_data = json.dumps(paper)
        cursor.execute('INSERT INTO papers (id, data) VALUES (?, ?)', (paper['id'], json_data))
except:
    write_progress(index)
    raise

# Commit changes and close the connection
conn.commit()
conn.close()
