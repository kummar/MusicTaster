# coding=utf-8

"""
Created by jayvee on 17/2/19.
https://github.com/JayveeHe
"""
import json
import string

import re
from flask import Flask, render_template, request, make_response

import os

import sys

abs_path = os.path.dirname(os.path.abspath(__file__))
abs_father_path = os.path.dirname(abs_path)
PROJECT_PATH = abs_father_path
print 'Used file: %s\nProject path=%s' % (__file__, PROJECT_PATH)
sys.path.append(PROJECT_PATH)

from song2vec.song2vec_operator import Song2VecOperator

from utils.logger_utils import data_process_logger

app = Flask(__name__)

data_process_logger.info('initing song2vec operator')
s2v_operator = Song2VecOperator(
    song2vec_model_path='%s/datas/[full_reduced]50d_20iter_10win_5min_song2vec.model' % PROJECT_PATH,
    artist2vec_model_path='%s/datas/[full_reduced]50d_20iter_10win_5min_artist2vec.model' % PROJECT_PATH)
data_process_logger.info('complete init song2vec')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/similar/song', methods=['POST'])
@app.route('/similar/song/<song_name>', methods=['GET'])
def query_similar_songs(song_name=None):
    try:
        if request.method == 'GET':
            top_n = int(request.args.get('top_n')) if request.args.get('top_n') else 10
            sim_res = s2v_operator.song2vec_model.most_similar(song_name, topn=top_n)
        elif request.method == 'POST':
            req_data_obj = json.loads(request.data)
            # 获取各组加减信息,并取小写字母(英文)
            positive_songs = lower_array(req_data_obj.get('positive_songs')) if req_data_obj.get(
                'positive_songs') else []
            negative_songs = lower_array(req_data_obj.get('negative_songs')) if req_data_obj.get(
                'negative_songs') else []
            positive_artists = lower_array(req_data_obj.get('positive_artists')) if req_data_obj.get(
                'positive_artists') else []
            negative_artists = lower_array(req_data_obj.get('negative_artists')) if req_data_obj.get(
                'negative_artists') else []
            top_n = req_data_obj.get('top_n') if req_data_obj.get('top_n') else 10
            sim_res = s2v_operator.calc_song_artist_similar(positive_songs=positive_songs,
                                                            negative_songs=negative_songs,
                                                            positive_artists=positive_artists,
                                                            negative_artists=negative_artists,
                                                            topn=top_n)
        else:
            sim_res = []
        # parse similar result
        parsed_sim_res = [{'name': a[0], 'similarity': a[1]} for a in sim_res]
        result = {'code': 200, 'result': parsed_sim_res}
        resp = make_response(json.dumps(result, ensure_ascii=False), 200)
    except Exception, e:
        res = {'code': 400, 'error_msg': e}
        resp = make_response(json.dumps(res, ensure_ascii=False), 400)
    return resp


@app.route('/cluster/playlist/id/<plid>', methods=['GET'])
def cluster_playlist_by_plid(plid=None):
    try:
        if request.args.get('cluster_n'):
            cluster_n = eval(request.args.get('cluster_n'))
        else:
            cluster_n = 5
        cluster_res = s2v_operator.cluster_in_playlist(plid, cluster_n=cluster_n)
        result = {'code': 200, 'result': cluster_res}
        resp = make_response(json.dumps(result, ensure_ascii=False), 200)
    except Exception, e:
        res = {'code': 400, 'error_msg': e}
        resp = make_response(json.dumps(res, ensure_ascii=False), 400)
    return resp


@app.route('/cluster/playlist/url', methods=['POST'])
def cluster_playlist_by_url():
    try:
        url = json.loads(request.data)['url']
        plid = re.findall('\d{4,}', url)[0]
        if request.args.get('cluster_n'):
            cluster_n = eval(request.args.get('cluster_n'))
        else:
            cluster_n = 5
        cluster_res, playlist_name = s2v_operator.cluster_in_playlist(plid, cluster_n=cluster_n)
        result = {'code': 200, 'result': cluster_res, 'playlist_name': playlist_name}
        resp = make_response(json.dumps(result, ensure_ascii=False), 200)
    except Exception, e:
        res = {'code': 400, 'error_msg': e}
        resp = make_response(json.dumps(res, ensure_ascii=False), 400)
    return resp


def lower_array(arr):
    return [a.lower() for a in arr if isinstance(a, string)]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2335, debug=False)
