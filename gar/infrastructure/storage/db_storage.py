import sqlite3
import json
from infrastructure.database.db import DB_PATH

def save_encoding_to_db(name, encoding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    encoding_str = json.dumps(encoding.tolist())
    c.execute("INSERT INTO employees (name, encoding) VALUES (?, ?)", (name, encoding_str))
    conn.commit()
    conn.close()
