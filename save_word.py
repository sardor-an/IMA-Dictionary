import sqlite3

# Connect to the database
conn = sqlite3.connect("/home/sardor/Desktop/Project/instance/server.sqlite")
cursor = conn.cursor()

# Ensure the table exists
# cursor.execute("CREATE TABLE IF NOT EXISTS save_word (word TEXT UNIQUE NOT NULL)")

# Open the file and insert words efficiently
with open("words.txt", "r", encoding="utf-8") as file:
    words = [line.strip() for line in file.readlines()]

# Use executemany for bulk insertions
total_words = len(words)
batch_size = 1000  # Insert in batches to speed up

for i in range(0, total_words, batch_size):
    batch = [(word,) for word in words[i:i+batch_size]]
    cursor.executemany("INSERT OR IGNORE INTO Saved_word (word) VALUES (?)", batch)
    
    # Print log every batch
    print(f"Inserted {min(i+batch_size, total_words)}/{total_words} words...")

# Commit changes and close connection
conn.commit()
conn.close()

print("All words inserted successfully!")
