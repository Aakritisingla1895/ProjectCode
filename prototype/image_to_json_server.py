# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 11:09:32 2022

@author: Admin
"""

from model_properties_1 import ModelBuilder
from fastapi import FastAPI, UploadFile, File, Form
from PIL import Image
from io import BytesIO
import uvicorn
import numpy as np
import cv2 as cv2

app = FastAPI()

def load_image_into_numpy_array(data):
    npimg=np.frombuffer(data,np.uint8)
    frame=cv2.imdecode(npimg,cv2.IMREAD_COLOR)
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    	
    #return np.array(Image.open(BytesIO(data)))
    
@app.post("/")
async def read_root(file: UploadFile = File(...)):
    image = load_image_into_numpy_array(await file.read())
    
    class_checkpoint='prototype/weights/CharacterClass_effnet_SGD.pt'
    AMT_checkpoint='prototype/weights/CharacterProperties_effnet_adam.pt'
    shape_checkpoint='prototype/weights/MeasureProperties_effnet_b4_adam_50.pt'
    texture_checkpoint='prototype/weights/TextureProperties_effnet_b3_adam.pt'
    
    model=ModelBuilder(image,class_checkpoint,AMT_checkpoint,shape_checkpoint,texture_checkpoint)
    model_attributes=model.get_character_details()
    return {"ModelAttributes":model_attributes}

if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)    