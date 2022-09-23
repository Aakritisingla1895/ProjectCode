# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:07:45 2022

@author: Admin
"""

import bpy
import json
import os
from lib.blender.addons import BlendAddons
from lib.files.operations import FileOperations
from lib.blender.object import BlendObjects
from lib.blender.camera import BlenderCamera

class CreateCharacter():
    
    def __init__(self,json_path,output_folder,blender_file_path)->None:
        
        """
        Accepts json file containing information 
        about character name,age,mass,tone and the character's
        shape and texture.
        Uses that to create Mb-Lab character
        """
        self.json_file=json_path
        self.save_folder=output_folder
        self.obj_file=None
        self.uv_file=None
        
        self.character_json_dict={}
        self.character_dict={}
        self.body_measures_dict={}
        self.skin_dict={}
        
        self.blender_file=blender_file_path
        self.file_operations=FileOperations()
        self.mesh=None
    
    def activate_addons(self):
        blend_addons=BlendAddons()
        blend_addons.activate()
    
    def deactivate_addons(self):
        blend_addons=BlendAddons()
        blend_addons.deactivate()
    
    def create_blender_file(self):
        self.file_operations.create_blender_file(bpy,self.blender_file)
    
    def open_blender_file(self):
        self.file_operations.open_blender_file(bpy,self.blender_file)
    
    def save_blender_file(self):
        self.file_operations.save_blender_file(bpy,self.blender_file)
    
    def remove_all_objects_from_scene(self,blend_objects:BlendObjects):
        blend_objects.delete_all_objects()
    
    def cleanup_and_save(self):
        self.save_blender_file()
        self.file_operations.delete_all_backup_blender_files_in_folder(self.save_folder)
    def clean_data_folder(self):
        self.file_operations.delete_all_files_in_folder(self.save_folder)
    
    def setup_blender(self):
        self.clean_data_folder()
        self.create_blender_file()
        self.open_blender_file()
        blend_objects=BlendObjects(bpy)
        self.remove_all_objects_from_scene(blend_objects)
        self.save_blender_file()
        self.open_blender_file()
        self.activate_addons()
        bpy.context.preferences.addons.get('MB-Lab', None) 
        BlenderCamera(bpy)
    
    def create_character_object(self):
        print("reading character parameters \n")
        
        with open(self.json_file) as f:
            data=json.load(f)
        
        for i in data[0]:
            if 'character' in i:
                self.character_dict[i]=data[0][i]
        self.body_measures_dict=data[1]
        self.skin_dict=data[2]
    
    def intiate_character(self):
        print("Initiating character in blender \n")
        character_name = self.character_dict['character_name']
        self.render_engines='CYCLES'
        self.mblab_use_cycles=True
        self.mblab_use_muscle=True
        self.mblab_use_ik=False
        self.mblab_use_lamps=True
        self.bone_armature=None
        self.muscle_armature=None
        self.mesh=None
        self.armature_name=""
        if(bpy.context.mode!='OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT') #swicth back to Object Mode
        scn = bpy.context.scene
        scn.render.engine = self.render_engine
        scn.mblab_use_cycles=self.mblab_use_cycles
        scn.mblab_use_muscle=self.mblab_use_muscle
        scn.mblab_use_ik=self.mblab_use_ik        
        scn.mblab_character_name=character_name
        scn.mblab_use_lamps = self.mblab_use_lamps
        bpy.ops.mbast.init_character()  
        self.bone_armature = bpy.data.objects[character_name+"_skeleton"]
        self.muscle_armature = bpy.data.armatures['MBLab_skeleton_muscle_fk']
        self.muscle_armature.layers[0] = False
        self.muscle_armature.layers[1] = False
        self.muscle_armature.display_type = 'WIRE'
        bpy.show_in_front = False
        bpy.context.object.display_type = 'SOLID'
    
    def set_body_properties(self):
        bpy.ops.mbast.button_parameters_on()
        for i in self.body_measures_dict:
            parameter=i
            parameter_value=self.body_measures_dict[parameter]
            parent=parameter.split("_")[0]
            self.update_body_properties(parent,parameter,parameter_value)
        bpy.ops.mbast.button_parameters_off()
    
    def update_body_properties(self,parent,parameter,parameter_value):
        print("Updating character body properties in blender  "+ parent +" --> " + parameter +" \n") 
        bpy.context.scene.morphingCategory=parent
        bpy.data.objects[self.character_dict['character_name']][parameter]=parameter_value
    
    def set_skin_properties(self):
        bpy.ops.mbast.button_skin_on()
        for  i in self.skin_dict:
            print("Updating character skin properties in blender   "+" --> "+ i +" \n") 
            bpy.context.object[i]=self.skin_dict[i]
        bpy.ops.mbast.button_skin_off()
    
    def create_character(self):
        
        self.intiate_character()
        character_name=self.character_dict['character_name']
        bpy.data.objects[character_name].character_age=float(self.character_dict['character_age'])
        bpy.data.objects[character_name].character_tone=float(self.character_dict['character_tone'])
        bpy.data.objects[character_name].character_mass=float(self.character_dict['character_mass'])
        
        self.set_body_properties()
        self.set_skin_properties()
        
        self.finalize_character()
        
        for ob in bpy.data.objects:
            if 'MBlab_sk' in ob.name:
                self.bone_armature=bpy.data.objects[ob.name]
                self.armature_name=ob.name
            elif 'MBlab_bd' in ob.name:
                self.mesh=bpy.data.objects[ob.name]
                print('Mesh is ' + ob.name) 
    
    def finalize_character(self):
        bpy.ops.mbast.button_finalize_on()
        bpy.context.scene.mblab_save_images_and_backup=False
        bpy.ops.mbast.finalize_character()
        bpy.ops.mbast.button_finalize_off()
        print("Finalizing character in blender \n")
        self.save_blender_file()
    
    def export_final_files(self):
        if(bpy.context.mode!='OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active=self.mesh
        target_file=os.path.join(self.save_folder,'character.obj')
        bpy.ops.export_scene.obj(filepath=target_file)
    
if __name__=="__main__":
    os.system('clear')
    output_folder='prototype/blender_file/'
    json_file='prototype/json_file/model65a.json'
    
    blender_file_path=output_folder+"/Model.blend"
    character=CreateCharacter(json_file, output_folder, blender_file_path)
    character.setup_blender()
    character.create_character_object()
    character.create_character()
    character.export_final_files()
    character.cleanup_and_save()
    character.deactivate_addons()
    
        