import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

# Environment variables (support multiple naming conventions)
USER = os.getenv('user') or os.getenv('SNOWFLAKE_USER')
PASSWORD = os.getenv('password') or os.getenv('SNOWFLAKE_PASSWORD')
ACCOUNT = os.getenv('account') or os.getenv('SNOWFLAKE_ACCOUNT')
WAREHOUSE = os.getenv('warehouse') or os.getenv('SNOWFLAKE_WAREHOUSE')
DATABASE = os.getenv('database') or os.getenv('SNOWFLAKE_DATABASE') or 'DASHBOARD'


def main():
    if not (USER and PASSWORD and ACCOUNT):
        print('Missing Snowflake credentials. Set SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT.')
        return

    conn = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        autocommit=False,
    )

    cursor = conn.cursor()
    try:
        cursor.execute(f"USE DATABASE {DATABASE}")

        # Create schemas if they don't exist
        schemas = ['TODOLIST', 'CALENDAR', 'COMPLIANCES']
        for s in schemas:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {s}")

        # Create tables
        cursor.execute('USE SCHEMA TODOLIST')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TODOS (
            ID VARCHAR PRIMARY KEY,
            TEXT VARCHAR,
            COMPLETED BOOLEAN DEFAULT FALSE,
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
        ''')

        cursor.execute('USE SCHEMA CALENDAR')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CALENDAR_ITEMS (
            ID VARCHAR PRIMARY KEY,
            TITLE VARCHAR,
            DATE DATE,
            DESCRIPTION VARCHAR,
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
        ''')

        cursor.execute('USE SCHEMA COMPLIANCES')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS COMPLIANCE_ITEMS (
            ID VARCHAR PRIMARY KEY,
            TEXT VARCHAR,
            COMPLETED BOOLEAN DEFAULT FALSE,
            DUE_DATE DATE,
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
        ''')

        conn.commit()
        print('Schemas and tables created (or already existed).')

    except Exception as e:
        print('Error creating schemas/tables:', e)
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
