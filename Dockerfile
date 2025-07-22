# Base image officielle Python
FROM python:3.10-slim

# Crée un répertoire dans le conteneur
WORKDIR /app

# Copie les fichiers locaux dans le conteneur
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer l'app
CMD ["streamlit", "run", "code.py", "--server.port=8501", "--server.address=0.0.0.0"]
