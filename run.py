from servFunc import app
from flask_cors import CORS
from flask import jsonify
from flask import request
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

@app.route("/login", methods=["POST"])
def login():
    id = request.args.get("id")
    pw = request.args.get("pw")
    if id != "admin" or pw != "1234": #임의 값 입니당
        return jsonify({"msg": "Bad id or pw"}), 401
    
    delta = datetime.timedelta(minutes=15) #유효기간 15분
    access_token = create_access_token(identity=id, expires_delta = delta)
    return jsonify(access_token=access_token)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))