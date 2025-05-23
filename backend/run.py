from app import create_app

# Abstract the app object
app = create_app()

if __name__ == "__main__":
    app.run (debug=True)