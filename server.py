#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# WebCam Streaming
#
# created by Keisuke Okumura

import os
from bottle import route, run, view, get, HTTPResponse, request, static_file
from bottle import TEMPLATE_PATH
import atexit
import cv2
from camera import Camera
from calibration import Calibration


CAMERA = Camera(use_last=False, image_width=640, image_height=480)
CALIBRATION = Calibration()


# PATHの設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH.append(BASE_DIR + "/views")


# 終了ハンドラ
def end_handler():
    CAMERA.capture.release()


# OpenCVのフィルター
def filter(image, type):
    if type == "grayscale":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif type == "undistort":
        image = cv2.undistort(image, CALIBRATION.mtx, CALIBRATION.dist,
                              None, CALIBRATION.newcameramtx)
    elif type == "mirror":
        image = cv2.flip(image, 1)
    elif type == "blur":
        image = cv2.GaussianBlur(image, (15, 15), 0)
    return image


# 以下、サーバー設定
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
    type = request.query.type if request.query.type else None
    return dict(type=type)


@route('/snapshot')
@route('/snapshot/<num>')
def snapshot(num=0):
    ret, image = CAMERA.capture.read()
    if not ret:
        return HTTPResponse(status=400, body="ERROR")
    if request.query.type:
        image = filter(image, request.query.type.split('/')[0])
    cv2.imwrite(BASE_DIR+"/static/images/snapshot/img.jpg", image)
    return static_file("img.jpg", root=BASE_DIR+"/static/images/snapshot/")


if __name__ == '__main__':
    atexit.register(end_handler)
    PORT = 8080
    HOST = '0.0.0.0'
    run(host=HOST, port=PORT, reloader=True)
