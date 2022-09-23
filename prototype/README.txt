The following package includes code for obtaining model attributes from a single image.These attributes are then stored in
a json file,which is then used to create a model in blender using bpy
In order to reproduce the results please execute the following command
to create json from image
1.python image_to_json.py --image images/model_427_6.jpg --class_checkpoint weights/CharacterClass_effnet_SGD.pt --AMT_checkpoint weights/CharacterProperties_effnetB4_adam_no_weighted_orig52.pt --shape_checkpoint weights/MeasureProperties_effnet_b4_adam_50.pt --texture_checkpoint weights/TextureProperties_effnet_b3_adam.pt --json_path json_file/model_427.json

--image name of image
--class_checkpoint path to character class name model weight
--AMT_checkpoint path to Age mass tone model weight
--shape_checkpoint path to shape model weight
--texture_checkpoint path to texture model weight
--json_path path to where json file will be saved

to create blender file from json

2. python json_to_model.py


to create json from image on server
python image_to_json_server.py

then go to http://127.0.0.1:8000/docs in post section click try it out upload image and then in response json will be displayed.Download that json
Then execute step 2
