# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 10:58:24 2022

@author: Admin
"""

from torch import nn
import timm


def build_shape_model():
    model = timm.create_model('tf_efficientnet_b4_ns', pretrained=True)
    for param in model.parameters():
        param.requires_grad = False
    model.classifier = nn.Sequential(
        nn.Linear(in_features=1792, out_features=625),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(in_features=625, out_features=256),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(in_features=256, out_features=199)
    )
    return model
