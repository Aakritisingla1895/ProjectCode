# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 11:10:08 2022

@author: Admin
"""

import argparse

from matplotlib import image
from model_properties import ModelBuilder


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--image', type=str, default=None,
                        help='path to image')
    parser.add_argument('--class_checkpoint', type=str,
                        default=None, help='path to character_name_checkpoint')
    parser.add_argument('--AMT_checkpoint', type=str,
                        default=None, help='path to character_AMT_checkpoint')
    parser.add_argument('--shape_checkpoint', type=str,
                        default=None, help='path to shape  checkpoint')
    parser.add_argument('--texture_checkpoint', type=str,
                        default=None, help='path to texture checkpoint')
    parser.add_argument('--json_path', type=str,
                        default=None, help='path to JSON file')

    args = parser.parse_args()

    model = ModelBuilder(args.image, args.class_checkpoint, args.AMT_checkpoint,
                         args.shape_checkpoint, args.texture_checkpoint, args.json_path)
    model.get_character_details()


if __name__ == '__main__':

    main()
