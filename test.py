import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from deepface import DeepFace



objects = DeepFace.analyze(
    img_path = "uploads/g.jpg" ,
    actions=( "emotion" , "gender" , "race") , enforce_detection=False
)

print(objects[0]["dominant_race"]  , objects[0]["dominant_emotion"] , objects[0]["dominant_gender"] )

