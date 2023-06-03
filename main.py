from flask import Flask, jsonify, request, abort
from model import get_prediction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['TIMEOUT'] = 300

@app.after_request
def set_content_type(response):
    response.headers['Content-Type'] = 'application/json'
    return response

# @app.errorhandler(400)
# def handle_bad_request(error):
#     response = jsonify({'error': 'Bad Request', 'message':'User Not Found for given username'})
#     response.status_code = 400
#     print(error)
#     return response

@app.errorhandler(400)
def handle_bad_request(error):
    response = jsonify({'error': 'Bad Request', 'message': str(error)})
    response.status_code = 400
    return response

@app.errorhandler(500)
def handle_bad_request(error):
    response = jsonify({'error': 'Server Error'})
    response.status_code = 500
    print(error)
    return response

@app.route('/')
def root():
    return jsonify('Server Up and Running.')


@app.route('/predict/<string:username>', methods=["GET"])
def pridict_occupation(username):
    print(username)
    return get_prediction(username)
    # return username

# @app.route('/test')
# def test():
#     d = ["dadf"]
#     mad = { }

#     result = {
#         "counts" : d,
#         "predict" : "labeled"
#     }

#     # return jsonify(result)
#     return myFun()


if __name__=="__main__":
    app.run(host="0.0.0.0",port= 5000, debug=True)