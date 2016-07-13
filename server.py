#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# created by Keisuke Okumura

import os
from bottle import route, run, view, get, HTTPResponse, request, static_file
from bottle import TEMPLATE_PATH
import atexit
import cv2


# ===== CAMERA MATRIX ======


# ===== PATHの設定 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH.append(BASE_DIR + "/views")

# ===== WEBCAMの設定 =====
capture = cv2.VideoCapture(1)
capture.set(3, 640)  # width
capture.set(4, 480)  # height
capture.set(5, 5)    # FPS
if capture.isOpened() is False:
    raise("IO Error")


# ===== 終了ハンドラ =====
def end_handler():
    capture.release()


# ===== OpenCVのフィルター =====
def filter(image, type):
    if type == "grayscale":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


# ===== サーバー =====
@route('/css/<filename>')
def css_dir(filename):
    """CSSファイルのパス作成
    """
    return static_file(filename, root=BASE_DIR+"/static/css")


@route('/images/<filename>')
def images(filename):
    """IMAGEファイルのパス作成
    """
    return static_file(filename, root=BASE_DIR+"/static/images")


@route('/')
@view('index')
def index():
    return dict()


@route('/snapshot')
@route('/snapshot/<num>')
def snapshot(num=0):
    ret, image = capture.read()
    if not ret:
        return HTTPResponse(status=400, body="ERROR")
    if request.query.type:
        image = filter(image, request.query.type)
    cv2.imwrite(BASE_DIR+"/static/images/img.jpg", image)
    return static_file("img.jpg", root=BASE_DIR+"/static/images")


if __name__ == '__main__':
    atexit.register(end_handler)
    PORT = 8080
    HOST = '0.0.0.0'
    run(host=HOST, port=PORT, reloader=True)
