import os
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import cv2.data
from flask import Flask , render_template , request, redirect,session , url_for , make_response
import cv2
import asyncio
import dlib



app =Flask("face analysis")

# define some configs
app.config["UPLOAD_FOLDER"] = "static/uploads/" # folder which uploaded file will be saved in
app.config["ALLOWED_EXTENSIONS"] = {"png" , "jpg" , "jpeg"}
# app.config["FLASK_APP"] = "app.py"
# app.config["FLASK_ENV"]="development"



def auth(email , password):
    # if email == "k.jhnshid@gmail.com" and password == "1234" :
    #     return True
    # else :
    #     return False
    return True

def allowed_files(filename):
    return True


def predictor(upload_path):
    img = cv2.imread(upload_path) 
    frame = img.copy() 

    # ------------ Model for Age detection --------# 
    age_weights = "models/age_deploy.prototxt"
    age_config = "models/age_net.caffemodel"
    genderProto="models/gender_deploy.prototxt"
    genderModel="models/gender_net.caffemodel"
    faceProto="models/opencv_face_detector.pbtxt"
    faceModel="models/opencv_face_detector_uint8.pb"


    age_Net = cv2.dnn.readNet(age_config, age_weights) 
    faceNet=cv2.dnn.readNet(faceModel,faceProto)
    genderNet=cv2.dnn.readNet(genderModel,genderProto)

    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)'] 
    genderList=['Male','Female']

    model_mean = (78.4263377603, 87.7689143744, 114.895847746) 

    fH = img.shape[0] 
    fW = img.shape[1] 
    Boxes = [] # to store the face co-ordinates 
    mssg = 'Face Detected' # to display on image 

    # ------------- Model for face detection---------# 
    face_detector = dlib.get_frontal_face_detector() 
    # converting to grayscale 
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 

    faces = face_detector(img_gray) 
    if not faces: 
        mssg = 'No face detected'
        cv2.putText(img, f'{mssg}', (40, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (200), 2) 
        cv2.imshow('Age detected', img) 
        cv2.waitKey(0) 
        
    else: 
        # --------- Bounding Face ---------# 
        for face in faces: 
            x = face.left() # extracting the face coordinates 
            y = face.top() 
            x2 = face.right() 
            y2 = face.bottom() 

            # rescaling those coordinates for our image 
            box = [x, y, x2, y2] 
            Boxes.append(box) 
            cv2.rectangle(frame, (x, y), (x2, y2), 
                        (00, 200, 200), 2) 

        for box in Boxes: 
            face = frame[box[1]:box[3], box[0]:box[2]] 

            # ----- Image preprocessing --------# 
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), model_mean, swapRB=False) 

            # -------Age Prediction---------# 
            age_Net.setInput(blob) 
            age_preds = age_Net.forward() 
            age = ageList[age_preds[0].argmax()] 
            print(f'age: {age}')
            
            genderNet.setInput(blob)
            genderPreds=genderNet.forward()
            gender=genderList[genderPreds[0].argmax()]
            print(f'Gender: {gender}')

            cv2.putText(frame, f'{gender} , age:{age}', (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA) 
            cv2.imwrite("output.jpg", frame)
            return frame , age  , gender






@app.route("/" , methods=["GET"]) # its only GET (bc we dont want to send any info to backend)
def main_page():
    return render_template("index.html")


@app.route("/login" , methods=["GET" , "POST"]) # we have 2 situations
# get  : show login page
# post : post user information into backend server
def login():
    if request.method == "GET" :
        return render_template("login.html")
    elif request.method == "POST" : # an email and a password is going to send to backend
        # its a request from form part in login.html
        user_email = request.form["email"]
        user_pass = request.form["password"]

        # if email & pass are correct , user will be navigate to upload page
        result= auth(user_email , user_pass)
        if result :
            # we cant use this : return render_template("upload.html")
            return redirect(url_for("upload")) # go and run below upload function
        # if email or pass was wrong , user will be send back to login page
        else :
            return redirect(url_for("login"))


# get : for showing upload page to user
# post : when uploading an image
@app.route("/upload" , methods=["GET" ,"POST"])
def upload() :
    if request.method == "GET" :
        return make_response(render_template("upload.html"))

    elif request.method == "POST" :
       
            user_image = request.files["image"] # name of input tag was image in login file # uploaded file is in  ( request.files() )
            # check if file is uploaded correctly
            if user_image.filename == "" :
                return make_response(render_template("upload.html"))#redirect(url_for("upload"))
            else :
                if user_image  and  allowed_files(user_image.filename): # if image is not null , and check file postfix
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"] , user_image.filename)
                    user_image.save(upload_path) # save image in this path
                    upload_path  = str(upload_path)  
                    print(upload_path) 
                    image = cv2.imread(filename=upload_path)

                    final_image , age , gender =  predictor(upload_path)

                    save_path = os.path.join("static/uploads/", user_image.filename)
                    cv2.imwrite(save_path, final_image)
                    result = make_response(render_template("result.html" ,image_link= save_path ,  age=age , gender=gender))
                    return result

        

@app.route("/bmr" , methods=["GET" , "POST"])
def bmr_calc():
    if request.method == "GET" :
        return render_template("bmr.html")

    else :
        age = float( request.form["age"])
        weight = float( request.form["weight"])
        height = float( request.form["height"])
        gender = request.form["gender"]
        print(age , weight , height , gender)

        if gender == "female" or gender == "Female" :
            bmr_result = (10*weight) + (6.25*height) - (5*age) - 161
        
        elif gender == "male" or gender == "Male": 
            bmr_result = (10*weight) + (6.25*height) - (5*age) + 5


        return render_template("bmr.html" , bmr_result=bmr_result)



# how to run
# bc our main file is app.py , so ther is no need to use ""app"" word in command
# flask run --debug



# if __name__ == "__main__":
#     http_server = WSGIServer(('', 5000), app)
#     http_server.serve_forever()



# env:FLASK_ENV = "development"
# flask run