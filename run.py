from servFunc import app
from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')