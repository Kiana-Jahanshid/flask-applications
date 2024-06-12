import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from deepface import DeepFace



objects = DeepFace.analyze(
    img_path = "uploads/ME.jpg" ,
    actions=("age" , "emotion" , "gender") 
)

print(objects[0]["age"]  , objects[0]["dominant_emotion"] , objects[0]["dominant_gender"] )

