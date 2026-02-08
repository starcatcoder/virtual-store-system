import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Tabela produtos com estoque
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    image TEXT,
    stock INTEGER DEFAULT 0
)
""")

# Tabela usuários admin
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

# Cria admin padrão
try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
except sqlite3.IntegrityError:
    pass

conn.commit()
conn.close()
print("Banco e tabelas criados com estoque e admin!")
