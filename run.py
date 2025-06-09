from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

'''# app.py ou run.py
from app import create_app

# Développement (par défaut)
app = create_app()

# Ou spécifier l'environnement
app = create_app('development')
app = create_app('testing')
app = create_app('production')

if __name__ == '__main__':
    app.run(debug=True)'''
