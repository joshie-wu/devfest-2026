from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid
import os
from dotenv import load_dotenv
import snowflake.connector
from typing import Optional
import json
from datetime import date


load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Snowflake connection parameters from environment variables
SNOWFLAKE_USER = os.getenv('user') or os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('password') or os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('account') or os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('warehouse') or os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('database') or os.getenv('SNOWFLAKE_DATABASE') or 'DASHBOARD'


def get_snowflake_connection():
    """Create and return a Snowflake connection"""
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        autocommit=False,
    )


@app.get('/api/health')
def health():
    return JSONResponse({'status': 'ok'})


@app.get('/')
def root():
    return JSONResponse({'message': 'FastAPI backend running'})


@app.post('/api/upload')
async def upload_file(file: UploadFile = File(...)):
    uploads_dir = Path(__file__).resolve().parent / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # create a safe unique filename to avoid collisions
    suffix = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    dest = uploads_dir / unique_name

    try:
        with dest.open('wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        await file.close()

    # Return relative path (recommended) and filename
    rel_path = f"/uploads/{unique_name}"
    return JSONResponse({'filename': unique_name, 'path': rel_path})


# ============= TO-DO LIST ENDPOINTS =============

@app.get('/api/todos')
def get_todos():
    """Fetch all to-do items from Snowflake"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA TODOLIST')
        cursor.execute('SELECT ID, TEXT, COMPLETED FROM TODOS ORDER BY ID DESC')
        
        todos = [
            {'id': row[0], 'text': row[1], 'completed': row[2]}
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        return JSONResponse({'todos': todos})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch todos: {str(e)}")


@app.post('/api/todos')
def create_todo(item: dict):
    """Create a new to-do item in Snowflake"""
    try:
        if 'text' not in item or not item['text'].strip():
            raise HTTPException(status_code=400, detail="Todo text is required")
        
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA TODOLIST')
        todo_id = uuid.uuid4().hex
        text = item['text']
        completed = item.get('completed', False)
        
        cursor.execute(
            'INSERT INTO TODOS (ID, TEXT, COMPLETED) VALUES (%s, %s, %s)',
            (todo_id, text, completed)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'id': todo_id, 'text': text, 'completed': completed})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create todo: {str(e)}")


@app.put('/api/todos/{todo_id}')
def update_todo(todo_id: str, item: dict):
    """Update an existing to-do item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA TODOLIST')
        
        if 'text' in item:
            cursor.execute(
                'UPDATE TODOS SET TEXT = %s WHERE ID = %s',
                (item['text'], todo_id)
            )
        
        if 'completed' in item:
            cursor.execute(
                'UPDATE TODOS SET COMPLETED = %s WHERE ID = %s',
                (item['completed'], todo_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Todo updated successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update todo: {str(e)}")


@app.delete('/api/todos/{todo_id}')
def delete_todo(todo_id: str):
    """Delete a to-do item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA TODOLIST')
        cursor.execute('DELETE FROM TODOS WHERE ID = %s', (todo_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Todo deleted successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete todo: {str(e)}")


# ============= CALENDAR ENDPOINTS =============

@app.get('/api/calendar')
def get_calendar_items():
    """Fetch all calendar items from Snowflake"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA CALENDAR')
        cursor.execute('SELECT ID, TITLE, DATE, DESCRIPTION FROM CALENDAR_ITEMS ORDER BY DATE')
        
        items = [
            {'id': row[0], 'title': row[1], 'date': str(row[2]), 'description': row[3]}
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        return JSONResponse({'items': items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar items: {str(e)}")


@app.post('/api/calendar')
def create_calendar_item(item: dict):
    """Create a new calendar item in Snowflake"""
    try:
        required_fields = ['title', 'date']
        if not all(field in item for field in required_fields):
            raise HTTPException(status_code=400, detail=f"Required fields: {', '.join(required_fields)}")
        
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA CALENDAR')
        item_id = uuid.uuid4().hex
        
        cursor.execute(
            'INSERT INTO CALENDAR_ITEMS (ID, TITLE, DATE, DESCRIPTION) VALUES (%s, %s, %s, %s)',
            (item_id, item['title'], item['date'], item.get('description', ''))
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'id': item_id, **item})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar item: {str(e)}")


@app.put('/api/calendar/{item_id}')
def update_calendar_item(item_id: str, item: dict):
    """Update a calendar item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA CALENDAR')
        
        if 'title' in item:
            cursor.execute('UPDATE CALENDAR_ITEMS SET TITLE = %s WHERE ID = %s', (item['title'], item_id))
        if 'date' in item:
            cursor.execute('UPDATE CALENDAR_ITEMS SET DATE = %s WHERE ID = %s', (item['date'], item_id))
        if 'description' in item:
            cursor.execute('UPDATE CALENDAR_ITEMS SET DESCRIPTION = %s WHERE ID = %s', (item['description'], item_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Calendar item updated successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update calendar item: {str(e)}")


@app.delete('/api/calendar/{item_id}')
def delete_calendar_item(item_id: str):
    """Delete a calendar item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA CALENDAR')
        cursor.execute('DELETE FROM CALENDAR_ITEMS WHERE ID = %s', (item_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Calendar item deleted successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete calendar item: {str(e)}")


# ============= COMPLIANCE ENDPOINTS =============

@app.get('/api/compliances')
def get_compliance_items():
    """Fetch all compliance items from Snowflake"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA COMPLIANCES')
        cursor.execute('SELECT ID, TEXT, COMPLETED FROM COMPLIANCE_ITEMS ORDER BY ID DESC')
        
        items = [
            {'id': row[0], 'text': row[1], 'completed': row[2]}
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        return JSONResponse({'items': items})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch compliance items: {str(e)}")


@app.post('/api/compliances')
def create_compliance_item(item: dict):
    """Create a new compliance item in Snowflake"""
    try:
        if 'text' not in item or not item['text'].strip():
            raise HTTPException(status_code=400, detail="Compliance text is required")
        
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA COMPLIANCES')
        item_id = uuid.uuid4().hex
        text = item['text']
        completed = item.get('completed', False)
        
        cursor.execute(
            'INSERT INTO COMPLIANCE_ITEMS (ID, TEXT, COMPLETED) VALUES (%s, %s, %s)',
            (item_id, text, completed)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'id': item_id, 'text': text, 'completed': completed})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create compliance item: {str(e)}")


@app.put('/api/compliances/{item_id}')
def update_compliance_item(item_id: str, item: dict):
    """Update a compliance item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA COMPLIANCES')
        
        if 'text' in item:
            cursor.execute('UPDATE COMPLIANCE_ITEMS SET TEXT = %s WHERE ID = %s', (item['text'], item_id))
        
        if 'completed' in item:
            cursor.execute('UPDATE COMPLIANCE_ITEMS SET COMPLETED = %s WHERE ID = %s', (item['completed'], item_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Compliance item updated successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update compliance item: {str(e)}")


@app.delete('/api/compliances/{item_id}')
def delete_compliance_item(item_id: str):
    """Delete a compliance item"""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        cursor.execute('USE SCHEMA COMPLIANCES')
        cursor.execute('DELETE FROM COMPLIANCE_ITEMS WHERE ID = %s', (item_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({'message': 'Compliance item deleted successfully'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete compliance item: {str(e)}")


@app.post('/api/test-snowflake')
def test_snowflake():
    """Run a quick insert test into each schema (TODOLIST, CALENDAR, COMPLIANCES)
    Returns inserted IDs on success or error details."""
    if not (SNOWFLAKE_USER and SNOWFLAKE_PASSWORD and SNOWFLAKE_ACCOUNT):
        raise HTTPException(status_code=400, detail='Missing Snowflake credentials in environment')

    conn = None
    cursor = None
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Ensure warehouse is set for the session
        if SNOWFLAKE_WAREHOUSE:
            cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
        else:
            raise HTTPException(status_code=400, detail='No warehouse selected. Set SNOWFLAKE_WAREHOUSE env var')

        # Ensure database
        cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")

        # Insert into TODOLIST schema
        cursor.execute('USE SCHEMA TODOLIST')
        todo_id = uuid.uuid4().hex
        cursor.execute(
            'INSERT INTO TODOS (ID, TEXT, COMPLETED) VALUES (%s, %s, %s)',
            (todo_id, 'API test todo', False)
        )

        # Insert into CALENDAR schema
        cursor.execute('USE SCHEMA CALENDAR')
        cal_id = uuid.uuid4().hex
        today = date.today().isoformat()
        cursor.execute(
            'INSERT INTO CALENDAR_ITEMS (ID, TITLE, DATE, DESCRIPTION) VALUES (%s, %s, %s, %s)',
            (cal_id, 'API test event', today, 'Inserted by API test')
        )

        # Insert into COMPLIANCES schema
        cursor.execute('USE SCHEMA COMPLIANCES')
        comp_id = uuid.uuid4().hex
        cursor.execute(
            'INSERT INTO COMPLIANCE_ITEMS (ID, TEXT, COMPLETED) VALUES (%s, %s, %s)',
            (comp_id, 'API test compliance', False)
        )

        conn.commit()
        return JSONResponse({'todo_id': todo_id, 'calendar_id': cal_id, 'compliance_id': comp_id})

    except HTTPException:
        # re-raise to be handled by FastAPI
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Error during test inserts: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass