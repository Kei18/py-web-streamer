#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Camera Calibration
# 参考 : http://russeng.hatenablog.jp/entry/2015/06/16/004704
#
# created by Keisuke Okumura

import pickle
import numpy as np
import cv2
from glob import glob
from camera import Camera


class Calibration(object):
    """カメラの内部パラメーターを操作するクラス
    """

    def __init__(self):
        # チェスボードの設定
        self.square_size = 21.0     # 正方形のサイズ
        self.pattern_size = (9, 6)  # 模様のパターン
        # 画像パス
        self.img_path = "./static/images/calibration/"
        self.pickle_path = "./pickle/calibration.pickle"
        # カメラキャリブレーションの変数
        self.ret = 0
        self.mtx = np.array([])
        self.dist = np.array([]),
        self.rvecs = 0
        self.tvecs = 0
        self.roi = 0
        self.newcameramtx = 0
        # データをセット
        self.load_data()

    # ================================
    # カメラの内部パラメーターを求め、
    # 保存するところまで一括で処理する
    # ================================
    def set_data(self):
        self.set_camera_params()
        img = cv2.imread(glob(self.img_path+"*.png")[0])
        h, w = img.shape[:2]
        self.get_newcameramatrix(w, h)
        self.generate_pickle()

    # ================================
    # カメラの内部パラメーターを求める
    # ================================
    def set_camera_params(self):
        print 'start calibration'
        # チェスボード（X,Y,Z）座標の指定 (Z=0)
        pattern_points = np.zeros((np.prod(self.pattern_size), 3), np.float32)
        pattern_points[:, :2] = np.indices(self.pattern_size).T.reshape(-1, 2)
        pattern_points *= self.square_size
        obj_points = []
        img_points = []

        for fn in glob(self.img_path+"*.png"):
            # 画像の取得
            im = cv2.imread(fn, 0)
            # チェスボードのコーナーを検出
            found, corner = cv2.findChessboardCorners(im, self.pattern_size)
            # コーナーがあれば
            if found:
                term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
                cv2.cornerSubPix(im, corner, (5, 5), (-1, -1), term)
            # コーナーがない場合のエラー処理
            if not found:
                print 'chessboard not found'
                continue
            # appendメソッド：リストの最後に因数のオブジェクトを追加
            img_points.append(corner.reshape(-1, 2))
            obj_points.append(pattern_points)
            # corner.reshape(-1, 2) : 検出したコーナーの画像内座標値(x, y)

            # 内部パラメータを計算
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(
            obj_points,
            img_points,
            (im.shape[1], im.shape[0]))
        print 'finish calibration'

    # ================================
    # カメラ行列を求める
    # ================================
    def get_newcameramatrix(self, width, height):
        self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
            self.mtx, self.dist, (width, height), 1, (width, height))

    # ================================
    # カメラパラメーターのPICKLEを生成
    # ================================
    def generate_pickle(self):
        obj = {
            'ret': self.ret,
            'mtx': self.mtx,
            'dist': self.dist,
            'newcameramtx': self.newcameramtx,
            'roi': self.roi,
            'rvecs': self.rvecs,
            'tvecs': self.tvecs,
        }
        with open(self.pickle_path, mode='wb') as f:
            pickle.dump(obj, f)

    # ================================
    # カメラパラメーターのPICKLEを解凍
    # ================================
    def load_data(self):
        try:
            with open(self.pickle_path, mode='rb') as f:
                obj = pickle.load(f)
            self.ret = obj['ret']
            self.mtx = obj['mtx']
            self.dist = obj['dist']
            self.newcameramtx = obj['newcameramtx']
            self.roi = obj['roi']
            self.rvecs = obj['rvecs']
            self.tvecs = obj['tvecs']
            print 'finish loading data'
        except:
            print """%s does not exist... You have to do camera calibration!
            """ % self.pickle_path


if __name__ == '__main__':
    print 'Now, let\'s start camera calibration.'
    CAMERA = Camera()
    CALIBRATION = Calibration()
    CAMERA.calibrate_shot()
    CALIBRATION.set_data()
