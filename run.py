"""
Point d'entrée de l'application Flask
Lance le serveur de développement
"""
from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("  Tableau de bord d'analyse de mobilité en France")
    print("="*60)
    print("\nApplication démarrée sur : http://localhost:8080")
    print("\nAppuyez sur CTRL+C pour arrêter le serveur\n")

    app.run(debug=True, host='0.0.0.0', port=8080)
