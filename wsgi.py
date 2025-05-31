'''# wsgi.py
from app import create_app
#from app.config import ProductionConfig  # Force la config production
#config_class=ProductionConfig
app = create_app()

if __name__ == "__main__":
    app.run()'''

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))