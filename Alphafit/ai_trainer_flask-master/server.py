import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restplus import Resource, Api, reqparse
from urllib.parse import urlsplit, parse_qsl

from ai_trainer import PersonalTrainer
import utils as ut

sys.path.append('inference')

base_dir = os.path.split(os.path.realpath(__file__))[0]
static_dir = os.path.join(base_dir, 'static')
app = Flask(__name__, static_folder=static_dir)
CORS(app)
api = Api(app=app)
results = []

pt = PersonalTrainer({'squat': 'NeckY', 'pushup': 'NeckY'}, auto_start=True, )


@app.route("/", methods=['GET'])
def home():
    return "API SERVER READY (HEALTH CHECKED)"


@app.route("/analyze/<file_name>")
def analyze(file_name):
    # =====[ Analyze squat data to pull out normalized, spliced reps ]=====
    squats = pt.analyze_reps('squat', file_name)

    # =====[ Extract feature vectors from squats for each exercise componenet  ]=====
    squat_feature_vectors = pt.get_prediction_features_opt('squat', squats)
    # pushup_feature_vectors = pt.get_prediction_features_opt('pushup',pushups)

    results = {}
    # =====[ Run classification on each squat component and report results  ]=====
    for key in squat_feature_vectors:
        x = squat_feature_vectors[key]
        classification = pt.classify('squat', key, x)
        results[key] = classification

    return results


def advice():
    analyzed_result = analyze('squatData.txt')
    output_advice = pt.get_advice('squat', analyzed_result)
    return output_advice


#@app.route("/get_advice", methods=['GET'])
class GetAdvice(Resource):
    def post(self):
        advice_file = open('advice_file.txt', 'wb')
        return advice_file.read()


#@app.route("/analyze_raw", methods=['POST'])
class AnalyzeRaw(Resource):

    def post(self):
        req_data = request.get_json()
        to_write = open('squatData.txt', 'wb')
        to_write.write(req_data['data'].encode("utf-8"))
        ut.print_success('Data written to file')
        json_res = jsonify(advice())
        ut.print_success('Advice file generated')
        return json_res


api.add_resource(AnalyzeRaw, '/analyze_raw')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
