# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 14:33:06 2022

@author: Admin
"""

import torch
import torchvision
from torchvision import transforms
import torch.nn.functional as F

import numpy as np
import cv2
from PIL import Image
import json
import argparse
from sklearn.metrics import mean_squared_error
import time
from prototype.models.build_effnet import build_name_model
from prototype.models.build_effnet_age import build_age_model
from prototype.models.build_effnet_texture import build_texture_model
from prototype.models.build_effnet_shape import build_shape_model

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class ModelBuilder():

    def __init__(self, image, weight_name_path, weight_AMT_path, weight_shape_path, weight_texture_path):
        self.image = image
        self.weight_path1 = weight_name_path
        self.weight_path2 = weight_AMT_path
        self.weight_path3 = weight_shape_path
        self.weight_path4 = weight_texture_path

        self.model_character_name = build_name_model()
        self.model_character_AMT = build_age_model()
        self.model_character_shape = build_shape_model()
        self.model_character_texture = build_texture_model()

        self.character = {}
        self.measures = {}
        self.texture = {}

        

    def get_character_details(self):
        processed_img = self.process_image(self.image)
        print("\n  Step 1: Processing uploaded image \n")
        self.predict_character_name(processed_img, self.weight_path1)
        print("\n  Step 2.1: Estimated Character Race \n")
        self.predict_character_AMT(processed_img, self.weight_path2)
        print("\n  Step 2.2: Estimated Character Modifiers  - Age Mass Tone \n")
        self.predict_character_shape(processed_img, self.weight_path3)
        print("\n  Step 2.3: Estimated Character Body Parameters - Stomach Jaw Head \n")
        self.predict_character_texture(processed_img, self.weight_path4)
        print("\n  Step 2.3: Estimated Character Texture Parameters \n")
        return self.write_to_json()
        print("\n Step 3: Writing to JSON FILE \n")

    def process_image(self, image):
        image_transforms = {
            "test": transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [
                                     0.229, 0.224, 0.225])
            ])
        }
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        return image_transforms["test"](image)

    def predict_character_name(self, image, weight_path):
        class_name = ['F_AF', 'F_AS', 'F_CA',
                      'F_LA', 'M_AF', 'M_AS', 'M_CA', 'M_LA']
        idx_to_class = {i: j for i, j in enumerate(class_name)}
        class_to_idx = {value: key for key, value in idx_to_class.items()}

        self.model_character_name.load_state_dict(
            torch.load(weight_path, map_location='cpu'))
        self.model_character_name.eval()
        self.model_character_name.to(device)

        with torch.no_grad():
            ps = self.model_character_name(image.unsqueeze(0))
            ps = F.softmax(ps, dim=1)
            topk, topclass = ps.topk(1, dim=1)
        x = topclass.view(-1).cpu().numpy()
        label = idx_to_class[x[0]]
        label = label.lower()+"01"
        self.character['character_name'] = label

    def predict_character_AMT(self, image, weight_path):

        self.model_character_AMT.load_state_dict(
            torch.load(weight_path, map_location='cpu'))
        self.model_character_AMT.eval()
        self.model_character_AMT.to(device)

        with torch.no_grad():
            ps = self.model_character_AMT(image.unsqueeze(0))
        ps = ps.cpu().numpy().squeeze()
        self.character['character_age'] = str(ps[0])
        self.character['character_tone'] = str(ps[1])
        self.character['character_mass'] = str(ps[2])

    def predict_character_shape(self, image, weight_path):

        self.model_character_shape.load_state_dict(
            torch.load(weight_path, map_location='cpu'))
        self.model_character_shape.eval()
        self.model_character_shape.to(device)

        with torch.no_grad():
            predicted_shape = self.model_character_shape(image.unsqueeze(0))
        predicted_shape = predicted_shape.cpu().numpy().squeeze()

        self.measures["Abdomen_Mass"] = predicted_shape[0]
        self.measures["Abdomen_Tone"] = predicted_shape[1]
        self.measures["Armpit_PosZ"] = predicted_shape[2]
        self.measures["Arms_ForearmLength"] = predicted_shape[3]
        self.measures["Arms_ForearmMass"] = predicted_shape[4]
        self.measures["Arms_ForearmSize"] = predicted_shape[5]
        self.measures["Arms_ForearmTone"] = predicted_shape[6]
        self.measures["Arms_UpperarmGirth"] = predicted_shape[7]
        self.measures["Arms_UpperarmLength"] = predicted_shape[8]
        self.measures["Arms_UpperarmMass"] = predicted_shape[9]
        self.measures["Arms_UpperarmSize"] = predicted_shape[10]
        self.measures["Arms_UpperarmTone"] = predicted_shape[11]
        self.measures["Body_Size"] = predicted_shape[12]
        self.measures["Cheeks_CreaseExt"] = predicted_shape[13]
        self.measures["Cheeks_InfraVolume"] = predicted_shape[14]
        self.measures["Cheeks_Mass"] = predicted_shape[15]
        self.measures["Cheeks_SideCrease"] = predicted_shape[16]
        self.measures["Cheeks_Tone"] = predicted_shape[17]
        self.measures["Cheeks_Zygom"] = predicted_shape[18]
        self.measures["Cheeks_ZygomPosZ"] = predicted_shape[19]
        self.measures["Chest_Girth"] = predicted_shape[20]
        self.measures["Chest_SizeX"] = predicted_shape[21]
        self.measures["Chest_SizeY"] = predicted_shape[22]
        self.measures["Chest_SizeZ"] = predicted_shape[23]
        self.measures["Chin_Cleft"] = predicted_shape[24]
        self.measures["Chin_Prominence"] = predicted_shape[25]
        self.measures["Chin_SizeX"] = predicted_shape[26]
        self.measures["Chin_SizeZ"] = predicted_shape[27]
        self.measures["Chin_Tone"] = predicted_shape[28]
        self.measures["Ears_Lobe"] = predicted_shape[29]
        self.measures["Ears_LocY"] = predicted_shape[30]
        self.measures["Ears_LocZ"] = predicted_shape[31]
        self.measures["Ears_RotX"] = predicted_shape[32]
        self.measures["Ears_Round"] = predicted_shape[33]
        self.measures["Ears_SizeX"] = predicted_shape[34]
        self.measures["Ears_SizeY"] = predicted_shape[35]
        self.measures["Ears_SizeZ"] = predicted_shape[36]
        self.measures["Elbows_Size"] = predicted_shape[37]
        self.measures["Eyebrows_Angle"] = predicted_shape[38]
        self.measures["Eyebrows_Droop"] = predicted_shape[39]
        self.measures["Eyebrows_PosZ"] = predicted_shape[40]
        self.measures["Eyebrows_Ridge"] = predicted_shape[41]
        self.measures["Eyebrows_SizeY"] = predicted_shape[42]
        self.measures["Eyebrows_Tone"] = predicted_shape[43]
        self.measures["Eyelids_Angle"] = predicted_shape[44]
        self.measures["Eyelids_Crease"] = predicted_shape[45]
        self.measures["Eyelids_InnerPosZ"] = predicted_shape[46]
        self.measures["Eyelids_LowerCurve"] = predicted_shape[47]
        self.measures["Eyelids_MiddlePosZ"] = predicted_shape[48]
        self.measures["Eyelids_OuterPosZ"] = predicted_shape[49]
        self.measures["Eyelids_SizeZ"] = predicted_shape[50]
        self.measures["Eyes_BagProminence"] = predicted_shape[51]
        self.measures["Eyes_BagSize"] = predicted_shape[52]
        self.measures["Eyes_Crosscalibration"] = predicted_shape[53]
        self.measures["Eyes_InnerPosX"] = predicted_shape[54]
        self.measures["Eyes_InnerPosZ"] = predicted_shape[55]
        self.measures["Eyes_IrisSize"] = predicted_shape[56]
        self.measures["Eyes_OuterPosX"] = predicted_shape[57]
        self.measures["Eyes_OuterPosZ"] = predicted_shape[58]
        self.measures["Eyes_PosX"] = predicted_shape[59]
        self.measures["Eyes_PosZ"] = predicted_shape[60]
        self.measures["Eyes_Size"] = predicted_shape[61]
        self.measures["Eyes_SizeZ"] = predicted_shape[62]
        self.measures["Eyes_TypeAlmond"] = predicted_shape[63]
        self.measures["Eyes_TypeHooded"] = predicted_shape[64]
        self.measures["Eyes_innerSinus"] = predicted_shape[65]
        self.measures["Face_Ellipsoid"] = predicted_shape[66]
        self.measures["Face_Parallelepiped"] = predicted_shape[67]
        self.measures["Face_Triangle"] = predicted_shape[68]
        self.measures["Feet_HeelWidth"] = predicted_shape[69]
        self.measures["Feet_Mass"] = predicted_shape[70]
        self.measures["Feet_Size"] = predicted_shape[71]
        self.measures["Feet_SizeX"] = predicted_shape[72]
        self.measures["Feet_SizeY"] = predicted_shape[73]
        self.measures["Feet_SizeZ"] = predicted_shape[74]
        self.measures["Forehead_Angle"] = predicted_shape[75]
        self.measures["Forehead_Curve"] = predicted_shape[76]
        self.measures["Forehead_SizeX"] = predicted_shape[77]
        self.measures["Forehead_SizeZ"] = predicted_shape[78]
        self.measures["Forehead_Temple"] = predicted_shape[79]
        self.measures["Hands_FingersDiam"] = predicted_shape[80]
        self.measures["Hands_FingersInterDist"] = predicted_shape[81]
        self.measures["Hands_FingersLength"] = predicted_shape[82]
        self.measures["Hands_FingersTipSize"] = predicted_shape[83]
        self.measures["Hands_Length"] = predicted_shape[84]
        self.measures["Hands_Mass"] = predicted_shape[85]
        self.measures["Hands_PalmLength"] = predicted_shape[86]
        self.measures["Hands_Size"] = predicted_shape[87]
        self.measures["Hands_Tone"] = predicted_shape[88]
        self.measures["Head_CraniumDolichocephalic"] = predicted_shape[89]
        self.measures["Head_CraniumPentagonoides"] = predicted_shape[90]
        self.measures["Head_CraniumPlatycephalus"] = predicted_shape[91]
        self.measures["Head_Flat"] = predicted_shape[92]
        self.measures["Head_Nucha"] = predicted_shape[93]
        self.measures["Head_Size"] = predicted_shape[94]
        self.measures["Head_SizeX"] = predicted_shape[95]
        self.measures["Head_SizeZ"] = predicted_shape[96]
        self.measures["Jaw_Angle"] = predicted_shape[97]
        self.measures["Jaw_Angle2"] = predicted_shape[98]
        self.measures["Jaw_LocY"] = predicted_shape[99]
        self.measures["Jaw_Prominence"] = predicted_shape[100]
        self.measures["Jaw_ScaleX"] = predicted_shape[101]
        self.measures["Legs_AnkleSize"] = predicted_shape[102]
        self.measures["Legs_Bow"] = predicted_shape[103]
        self.measures["Legs_CalfGirth"] = predicted_shape[104]
        self.measures["Legs_KneeProminence"] = predicted_shape[105]
        self.measures["Legs_KneeSize"] = predicted_shape[106]
        self.measures["Legs_LowerThighGirth"] = predicted_shape[107]
        self.measures["Legs_LowerlegLength"] = predicted_shape[108]
        self.measures["Legs_LowerlegSize"] = predicted_shape[109]
        self.measures["Legs_LowerlegsMass"] = predicted_shape[110]
        self.measures["Legs_LowerlegsTone"] = predicted_shape[111]
        self.measures["Legs_UpperThighGirth"] = predicted_shape[112]
        self.measures["Legs_UpperlegInCurve"] = predicted_shape[113]
        self.measures["Legs_UpperlegLength"] = predicted_shape[114]
        self.measures["Legs_UpperlegSize"] = predicted_shape[115]
        self.measures["Legs_UpperlegsMass"] = predicted_shape[116]
        self.measures["Legs_UpperlegsTone"] = predicted_shape[117]
        self.measures["Mouth_CornersPosZ"] = predicted_shape[118]
        self.measures["Mouth_LowerlipExt"] = predicted_shape[119]
        self.measures["Mouth_LowerlipSizeZ"] = predicted_shape[120]
        self.measures["Mouth_LowerlipVolume"] = predicted_shape[121]
        self.measures["Mouth_PhiltrumProminence"] = predicted_shape[122]
        self.measures["Mouth_PhiltrumSizeX"] = predicted_shape[123]
        self.measures["Mouth_PhiltrumSizeY"] = predicted_shape[124]
        self.measures["Mouth_PosY"] = predicted_shape[125]
        self.measures["Mouth_PosZ"] = predicted_shape[126]
        self.measures["Mouth_Protusion"] = predicted_shape[127]
        self.measures["Mouth_SideCrease"] = predicted_shape[128]
        self.measures["Mouth_SizeX"] = predicted_shape[129]
        self.measures["Mouth_UpperlipExt"] = predicted_shape[130]
        self.measures["Mouth_UpperlipSizeZ"] = predicted_shape[131]
        self.measures["Mouth_UpperlipVolume"] = predicted_shape[132]
        self.measures["Neck_Angle"] = predicted_shape[133]
        self.measures["Neck_Back"] = predicted_shape[134]
        self.measures["Neck_Collarbone"] = predicted_shape[135]
        self.measures["Neck_Length"] = predicted_shape[136]
        self.measures["Neck_Mass"] = predicted_shape[137]
        self.measures["Neck_SideCurve"] = predicted_shape[138]
        self.measures["Neck_Size"] = predicted_shape[139]
        self.measures["Neck_Tone"] = predicted_shape[140]
        self.measures["Neck_TrapeziousSize"] = predicted_shape[141]
        self.measures["Nose_BallSizeX"] = predicted_shape[142]
        self.measures["Nose_BasePosZ"] = predicted_shape[143]
        self.measures["Nose_BaseShape"] = predicted_shape[144]
        self.measures["Nose_BaseSizeX"] = predicted_shape[145]
        self.measures["Nose_BaseSizeZ"] = predicted_shape[146]
        self.measures["Nose_BridgeSizeX"] = predicted_shape[147]
        self.measures["Nose_Curve"] = predicted_shape[148]
        self.measures["Nose_GlabellaPosZ"] = predicted_shape[149]
        self.measures["Nose_GlabellaSizeX"] = predicted_shape[150]
        self.measures["Nose_GlabellaSizeY"] = predicted_shape[151]
        self.measures["Nose_NostrilCrease"] = predicted_shape[152]
        self.measures["Nose_NostrilDiam"] = predicted_shape[153]
        self.measures["Nose_NostrilPosZ"] = predicted_shape[154]
        self.measures["Nose_NostrilSizeX"] = predicted_shape[155]
        self.measures["Nose_NostrilSizeY"] = predicted_shape[156]
        self.measures["Nose_NostrilSizeZ"] = predicted_shape[157]
        self.measures["Nose_PosY"] = predicted_shape[158]
        self.measures["Nose_SeptumFlat"] = predicted_shape[159]
        self.measures["Nose_SeptumRolled"] = predicted_shape[160]
        self.measures["Nose_SizeY"] = predicted_shape[161]
        self.measures["Nose_TipAngle"] = predicted_shape[162]
        self.measures["Nose_TipPosY"] = predicted_shape[163]
        self.measures["Nose_TipPosZ"] = predicted_shape[164]
        self.measures["Nose_TipSize"] = predicted_shape[165]
        self.measures["Nose_WingAngle"] = predicted_shape[166]
        self.measures["Nose_WingBackFlat"] = predicted_shape[167]
        self.measures["Nose_WingBump"] = predicted_shape[168]
        self.measures["Pelvis_CrotchDist"] = predicted_shape[169]
        self.measures["Pelvis_CrotchVolume"] = predicted_shape[170]
        self.measures["Pelvis_Girth"] = predicted_shape[171]
        self.measures["Pelvis_GluteusMass"] = predicted_shape[172]
        self.measures["Pelvis_GluteusSize"] = predicted_shape[173]
        self.measures["Pelvis_GluteusTone"] = predicted_shape[174]
        self.measures["Pelvis_Length"] = predicted_shape[175]
        self.measures["Pelvis_SizeX"] = predicted_shape[176]
        self.measures["Pelvis_SizeY"] = predicted_shape[177]
        self.measures["Shoulders_Length"] = predicted_shape[178]
        self.measures["Shoulders_Mass"] = predicted_shape[179]
        self.measures["Shoulders_PosZ"] = predicted_shape[180]
        self.measures["Shoulders_Size"] = predicted_shape[181]
        self.measures["Shoulders_SizeX"] = predicted_shape[182]
        self.measures["Shoulders_SizeX2"] = predicted_shape[183]
        self.measures["Shoulders_Tone"] = predicted_shape[184]
        self.measures["Stomach_LocalFat"] = predicted_shape[185]
        self.measures["Stomach_Volume"] = predicted_shape[186]
        self.measures["Torso_BellyPosZ"] = predicted_shape[187]
        self.measures["Torso_BreastMass"] = predicted_shape[188]
        self.measures["Torso_Dorsi"] = predicted_shape[189]
        self.measures["Torso_Length"] = predicted_shape[190]
        self.measures["Torso_Mass"] = predicted_shape[191]
        self.measures["Torso_SizeX"] = predicted_shape[192]
        self.measures["Torso_SizeY"] = predicted_shape[193]
        self.measures["Torso_Tone"] = predicted_shape[194]
        self.measures["Torso_ToracicCurve"] = predicted_shape[195]
        self.measures["Torso_Vshape"] = predicted_shape[196]
        self.measures["Waist_Size"] = predicted_shape[197]
        self.measures["Wrists_Size"] = predicted_shape[198]

    def predict_character_texture(self, image, weight_path):

        self.model_character_texture.load_state_dict(
            torch.load(weight_path, map_location='cpu'))
        self.model_character_texture.eval()
        self.model_character_texture.to(device)

        with torch.no_grad():
            predicted_texture = self.model_character_texture(
                image.unsqueeze(0))
        predicted_texture = predicted_texture.cpu().numpy().squeeze()

        self.texture["eyes_hue"] = predicted_texture[0]
        self.texture["eyes_iris_mix"] = predicted_texture[1]
        self.texture["eyes_saturation"] = predicted_texture[2]
        self.texture["eyes_value"] = predicted_texture[3]
        self.texture["nails_mix"] = predicted_texture[4]
        self.texture["skin_blush"] = predicted_texture[5]
        self.texture["skin_bump"] = predicted_texture[6]
        self.texture["skin_complexion"] = predicted_texture[7]
        self.texture["skin_freckles"] = predicted_texture[8]
        self.texture["skin_oil"] = predicted_texture[9]
        self.texture["skin_roughness"] = predicted_texture[10]
        self.texture["skin_sss"] = predicted_texture[11]
        self.texture["skin_veins"] = predicted_texture[12]

    def write_to_json(self):
        character_key = self.character.items()
        new_character = {str(key): str(val) for key, val in character_key}
        shape_key = self.measures.items()
        new_shape = {str(key): str(val) for key, val in shape_key}
        texture_key = self.texture.items()
        new_texture = {str(key): str(val) for key, val in texture_key}
        data = [new_character, new_shape, new_texture]
        return data