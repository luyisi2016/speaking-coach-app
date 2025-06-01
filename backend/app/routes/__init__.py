# Import routes to register them
from .transcribe import transcribe_bp
from .analyse import analyse_bp

blueprints = [transcribe_bp, analyse_bp]