from flask import Flask
from flask_cors import CORS
from src.routes import routes_blueprint
from flask import jsonify
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the values
port = os.getenv('port')

app = Flask(__name__)

cors = CORS(app, resources={
r"/*"
: {
"origins"
:
"*"
}}, expose_headers=
'AuthToken'
)

app.config['CORS_HEADERS'] = 'Content-Type'
app.register_blueprint(routes_blueprint)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"msg": "Server up!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port)
