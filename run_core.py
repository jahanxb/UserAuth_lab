"""Run the core authentication lab application on http://localhost:5000."""

from dotenv import load_dotenv

from core_app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
