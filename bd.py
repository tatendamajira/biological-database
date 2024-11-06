import sqlite3
from faker import Faker
import random

fake = Faker()

def add_biological_data(conn, sample_name, species, collection_date, collected_by, description):
    c = conn.cursor()
    c.execute('INSERT INTO biological_data (sample_name, species, collection_date, collected_by, description) VALUES (?, ?, ?, ?, ?)',
              (sample_name, species, collection_date, collected_by, description))
    conn.commit()

def generate_tuberculosis_data(db_path='biological_database.db'):
    conn = sqlite3.connect(db_path)
    try:
        for _ in range(100):  # Generate 100 entries
            sample_name = "TB Sample " + str(fake.random_int(min=1, max=9999))
            species = "Mycobacterium tuberculosis"
            collection_date = fake.date_between(start_date='-5y', end_date='today').strftime("%Y-%m-%d")
            collected_by = fake.name()
            description = "Isolated from " + random.choice(['lung tissue', 'lymph node', 'sputum'])
            add_biological_data(conn, sample_name, species, collection_date, collected_by, description)
    finally:
        conn.close()

if __name__ == "__main__":
    generate_tuberculosis_data()
