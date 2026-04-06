from flask import Flask, render_template, request
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'helmdb')
DB_USER = os.getenv('DB_USER', 'helmuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'helmpass')

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def init_db():
    """Initialize database table if it doesn't exist"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id SERIAL PRIMARY KEY,
                    visit_time TIMESTAMP,
                    ip_address VARCHAR(50)
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database initialization failed: {e}")

@app.route('/')
def home():
    """Home page - log visit and show count"""
    db_status = "Connected"
    visitor_count = 0
    
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            # Log this visit
            ip_address = request.remote_addr
            cur.execute(
                "INSERT INTO visitors (visit_time, ip_address) VALUES (%s, %s)",
                (datetime.now(), ip_address)
            )
            conn.commit()
            
            # Get total visitor count
            cur.execute("SELECT COUNT(*) FROM visitors")
            visitor_count = cur.fetchone()[0]
            
            cur.close()
            conn.close()
        except Exception as e:
            db_status = f"Error: {e}"
    else:
        db_status = "Disconnected"
    
    return render_template('index.html', 
                         db_status=db_status, 
                         visitor_count=visitor_count)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'flask-app'}, 200

# Initialize database on startup (runs with Gunicorn too)
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)