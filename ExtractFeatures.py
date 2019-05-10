import numpy as np
import pickle
import re
import os
import glob
from sklearn import preprocessing
from python_speech_features import mfcc
from python_speech_features import delta
from scipy.io.wavfile import read
from sklearn.mixture import GaussianMixture as GMM


def extract_features(voice,rate,n=2):
    """
    Extract 20 features from MFCC and 20 features from delta MFCC

    """
    mfcc_feat = mfcc(voice, rate)
    d_mfcc_feat = delta(mfcc_feat, n)
    full_feat = np.hstack((mfcc_feat, d_mfcc_feat))

    return full_feat


def generate_model(source_path):
    # vad/<subject>/<subject_1.wav>
    subject = re.split("[/.]+", source_path)[1]
    subject_dir = subject[0] + "/" + subject[1] + "/"
    file_list = glob.glob(subject_dir + "/*.wav")

    model_dest = "model/" + subject + "/"

    if not os.path.exists(model_dest):
        os.makedirs(model_dest)

    count = 1

    features = np.asarray(())
    for file in enumerate(file_list):
        sr, audio = read(subject_dir+file)

        fv = extract_features(audio, sr, 2)

        if features.size == 0:
            features = fv
        else:
            features = np.vstack((features, fv))

        if count == 5:
            gmm = GMM(n_components=16, max_iter=200, covariance_type='diag', n_init=3)
            gmm.fit(features)

            model = subject+".gmm"
            pickle.dump(gmm, open(model_dest + model, "wb"))
            print("modeling complete for speaker : {} with data point = {}".format(model, features.shape))
            count = 0
        count = count + 1
