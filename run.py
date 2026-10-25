import os
from app import create_app
from app.extensions import db

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.cli.command('seed-db')
def seed_database():
    """Seed the database with comprehensive demonstration data."""
    from scripts.seed_data import run_seed
    with app.app_context():
        run_seed()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
