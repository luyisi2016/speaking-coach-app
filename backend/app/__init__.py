from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import routes inside function in order to avoid circular imports of dependencies
    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app
