import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect('databasee.db')
cursor = conn.cursor()

# Query to count occurrences of each unique city
query = '''
SELECT city, COUNT(*) as count
FROM user
GROUP BY city
'''

cursor.execute(query)
results = cursor.fetchall()
conn.close()

df = pd.DataFrame(results, columns=['City', 'Count'])

print(df['City'][1])
x = plt.pie(df['Count'], labels=df['City'], autopct='%1.1f%%', startangle=140)
print(x)