#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# WebCamera Setting
#
# created by Keisuke Okumura

import cv2
import pickle
import time


class Camera(object):
    """WEBカメラの設定
    """

    def __init__(self, use_last=True, camera_num=0,
                 image_width=1280, image_height=720, fps=30):
        self.img_path = "./static/images/calibration/"
        self.pickle_path = "./pickle/camera.pickle"
        self.shot_count = 10
        self.camera_num = camera_num
        self.image_width = image_width
        self.image_height = image_height
        self.fps = fps
        # Webカメラの設定
        if use_last:
            self.load_data()
        else:
            self.generate_pickle()  # 設定をPICKLEに保存しておく
        self.capture = cv2.VideoCapture(self.camera_num)
        self.set_capture()

    # ================================
    # キャプチャーの用意
    # ================================
    def set_capture(self):
        self.capture.set(3, self.image_width)
        self.capture.set(4, self.image_height)
        self.capture.set(5, self.fps)
        if self.capture.isOpened() is False:
            raise IOError('Camera cannot open.')
        print 'finish setting camera'

    # ================================
    # WebカメラのPICKLEを生成
    # ================================
    def generate_pickle(self):
        obj = {
            'camera_num': self.camera_num,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'fps': self.fps
        }
        with open(self.pickle_path, mode='wb') as f:
            pickle.dump(obj, f)

    # ================================
    # WebカメラのPICKLEを解凍
    # ================================
    def load_data(self):
        try:
            with open(self.pickle_path, mode='rb') as f:
                obj = pickle.load(f)
            self.camera_num = obj['camera_num']
            self.image_width = obj['image_width']
            self.image_height = obj['image_height']
            self.fps = obj['fps']
            print 'finish loading data'
        except:
            print "%s does not exist..." % self.pickle_path

    # ================================
    # スナップショットを撮影
    # ================================
    def snapshot(self, name):
        ret, image = self.capture.read()
        if not ret:
            raise("IO Error")
        cv2.imshow('frame', image)
        cv2.waitKey(1)
        cv2.imwrite(self.img_path+name, image)

    # ================================
    # キャリブレーション用にスナップショットを
    # 何枚か撮影する
    # ================================
    def calibrate_shot(self):
        print """
        ======================================\n
        Start taking photos for calibration.
        After 5 sec, webcam will take %d photos by intervals of 3 sec.
        Preparing your chessboard!\n
        ======================================\n
        """ % self.shot_count
        time.sleep(5)
        for i in xrange(0, self.shot_count):
            self.snapshot("Image"+str(i)+".png")
            print "%d photos left..." % (self.shot_count - i - 1)
            time.sleep(3)
        cv2.destroyAllWindows()
        print "finish taking photos"
