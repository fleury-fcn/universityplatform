import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pyodbc
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    # Connexion SQL Server
    sqlserver_conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={os.getenv("SQLSERVER_HOST")};'
        f'DATABASE=OpenIsta;'
        f'UID={os.getenv("SQLSERVER_USER")};'
        f'PWD={os.getenv("SQLSERVER_PASSWORD")}'
    )
    
    # Connexion PostgreSQL
    pg_conn = psycopg2.connect(
        dbname='openista',
        user='fleury',
        password='NouveauMotDePasse123',
        host='localhost'
    )
    
    # Liste des tables à migrer
    tables = ['users', 'messages', 'documents']  # Ajoutez vos tables ici
    
    for table in tables:
        print(f"Migration de la table {table}...")
        
        # Récupération des données depuis SQL Server
        cursor_sql = sqlserver_conn.cursor()
        cursor_sql.execute(f"SELECT * FROM {table}")
        columns = [column[0] for column in cursor_sql.description]
        data = cursor_sql.fetchall()
        
        # Insertion dans PostgreSQL
        cursor_pg = pg_conn.cursor()
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        for row in data:
            try:
                cursor_pg.execute(
                    f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})",
                    row
                )
            except Exception as e:
                print(f"Erreur sur la table {table}: {e}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"{len(data)} lignes migrées dans {table}")
    
    pg_conn.close()
    sqlserver_conn.close()
    print("Migration terminée!")

if __name__ == '__main__':
    migrate_data()