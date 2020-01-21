from flask import jsonify
import json
import urllib
import sys
import os

input = sys.stdin.readline

PROD_URL = 'http://54.180.159.171/analyze_raw'
DEV_URL = 'http://localhost:5000/analyze_raw'


def test_api(mode):
    url = PROD_URL if mode == 0 else DEV_URL

    print("Target URL : " + url)
    print("1. 동작 데이터 파일 읽는 중")
    data_file = open("squatData13.txt", 'r')

    print("2. http 요청 객체 구성 중")
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    values = data_file.read()

    body = {"data": values}
    json_data = json.dumps(body)
    json_data_as_byte = json_data.encode('utf-8')
    req.add_header('Content-Length', len(json_data_as_byte))

    print("3. 피드백 데이터 수신 중")
    response = urllib.request.urlopen(req, json_data_as_byte)
    res_read = response.read().decode('utf-8')
    print(res_read)


if __name__ == '__main__':
    print("API 테스트 실행 모드를 입력하여 주세요 (0: prod / 1: dev) ")
    test_api(int(input()))
