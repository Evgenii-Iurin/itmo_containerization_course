import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def get_db_conn():
    """Get database connection."""
    db_url = os.environ.get(
        'DB_URL',
        f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
        f"db:5432/{os.environ.get('POSTGRES_DB', 'postgres')}"
    )
    return psycopg2.connect(db_url)

@app.route('/')
def index():
    return jsonify({'message': 'Flask server is running', 'status': 'ok'})

@app.route('/health')
def health():
    try:
        conn = get_db_conn()
        conn.cursor().execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/db/test')
def db_test():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_init")
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'status': 'success', 'table': 'test_init', 'count': count}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)

