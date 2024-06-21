import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import cv2.data
from flask import Flask , render_template , request, redirect,session , url_for , make_response
import cv2
import asyncio
# import dlib
from sqlmodel import Field , SQLModel ,Session , select , create_engine
from pydantic import BaseModel
from ultralytics import YOLO
import bcrypt
from deepface import DeepFace
import asgiref

# we used pydantic to """ check user information validation automatically""" 
# without pydantic we had to use lots of if condition to check them .
# pydantic models are used for validating user data
class RegisterModel(BaseModel):
    username : str 
    password : str
    city : str
    country : str
    first_name : str
    last_name : str
    email : str
    age : int 
    confirm_password : str

class LoginModel(BaseModel):
    username : str
    password : str
    confirm_password : str

class User(SQLModel , table=True):
    id : int = Field(default=None , primary_key=True)
    username : str = Field(index=True)
    password : str 
    city : str
    first_name : str 
    last_name : str 
    email : str 
    age : int 
    country : str 
    # join_time : str      




app =Flask("face analysis")
app.config["UPLOAD_FOLDER"] = "static/uploads/" # folder which uploaded file will be saved in
app.config["ALLOWED_EXTENSIONS"] = {"png" , "jpg" , "jpeg"}
app.secret_key = "me_secret"

engine = create_engine(url="sqlite:///./database.db" , echo=True)
SQLModel.metadata.create_all(engine)



def auth(email , password):
    # if email == "k.jhnshid@gmail.com" and password == "1234" :
    #     return True
    # else :
    #     return False
    return True


def allowed_files(filename):
    return True


# def predictor(upload_path):
    img = cv2.imread(upload_path) 
    frame = img.copy() 

    # ------------ Model for Age detection --------# 
    age_weights = "models/age_deploy.prototxt"
    age_config = "models/age_net.caffemodel"
    # genderProto="models/gender_deploy.prototxt"
    # genderModel="models/gender_net.caffemodel"
    # faceProto="models/opencv_face_detector.pbtxt"
    # faceModel="models/opencv_face_detector_uint8.pb"

    age_Net = cv2.dnn.readNet(age_config, age_weights) 
    # faceNet=cv2.dnn.readNet(faceModel,faceProto)
    # genderNet=cv2.dnn.readNet(genderModel,genderProto)

    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)'] 
    genderList=['Male','Female']
    model_mean = (78.4263377603, 87.7689143744, 114.895847746) 
    fH = img.shape[0] 
    fW = img.shape[1] 
    Boxes = [] # to store the face co-ordinates 
    mssg = 'Face Detected' # to display on image 

    # ------------- Model for face detection---------# 
    face_detector = dlib.get_frontal_face_detector() 
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    faces = face_detector(img_gray) 
    if not faces: 
        mssg = 'No face detected'
        cv2.putText(img, f'{mssg}', (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (200), 2) 
        cv2.imshow('Age detected', img) 
        cv2.waitKey(0) 
    else: 
        # --------- Bounding Face ---------# 
        for face in faces: 
            x = face.left() # extracting face coordinates 
            y = face.top() 
            x2 = face.right() 
            y2 = face.bottom() 

            # rescaling those coordinates 
            box = [x, y, x2, y2] 
            Boxes.append(box) 
            cv2.rectangle(frame, (x, y), (x2, y2), (00, 200, 200), 2) 

        for box in Boxes: 
            face = frame[box[1]:box[3], box[0]:box[2]] 
            # ----- Image preprocessing --------# 
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), model_mean, swapRB=False) 
            # -------Age Prediction---------# 
            age_Net.setInput(blob) 
            age_preds = age_Net.forward() 
            age = ageList[age_preds[0].argmax()] 
            print(f'age: {age}')
            
            # genderNet.setInput(blob)
            # genderPreds=genderNet.forward()
            # gender=genderList[genderPreds[0].argmax()]
            # print(f'Gender: {gender}')

            cv2.putText(frame, f'age:{age}', (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA) 
            cv2.imwrite("output.jpg", frame)
            return frame , age  #, gender



@app.route("/" , methods=["GET"])
def main_page():
    return render_template("index.html")


@app.route("/register" , methods=["GET","POST"])
def register():
    if request.method == "GET" :
        return render_template("register.html")
    elif request.method == "POST" :
        try:
            register_data = RegisterModel(username=request.form["username"] ,password=request.form['password'] , city=request.form["city"]  ,country=request.form["country"] , first_name=request.form["firstname"] , last_name=request.form["lastname"] , email=request.form["email"] , age=request.form["age"] , confirm_password=request.form["confirm_password"])#validating attributes type
            print(request.form["username"])
        except:
            print("type error")
            return redirect(url_for("register"))
        if register_data.confirm_password == register_data.password :
            with Session(engine) as db_session : # READ DATABASEcheck and check if entered username exists
                query = select(User).where(User.username == request.form["username"]) # or register_data.username
                result = db_session.exec(query).first()
            if not result :
                print(register_data.password)
                password_byte = register_data.password.encode("utf-8")
                hashed_password = bcrypt.hashpw(password_byte , bcrypt.gensalt())
                print(hashed_password)

                with Session(engine) as db_session :#WRITE TO DATABASE
                    new_user = User(username=request.form["username"] ,password=hashed_password  , city=request.form["city"] ,country=request.form["country"] , first_name=request.form["firstname"] , last_name=request.form["lastname"] , email=request.form["email"] , age=request.form["age"]  ) # create a user object
                    db_session.add(new_user) # adding this object to database
                    db_session.commit()
                    db_session.refresh(new_user)
                    print("your registration compleated successfully🎉")
                    return redirect(url_for("login"))
            else:
                print("This username is already taken , choose another one")
                return redirect(url_for("register"))
        else :
            print("confirm password doesnt match with password , try again ... ")
            return redirect(url_for("register"))



@app.route("/login" , methods=["GET" , "POST"]) 
def login():
    if request.method == "GET" :
        return render_template("login.html")
    elif request.method == "POST" : 
        try :            
            register_login_data = LoginModel(username=request.form["username"] , password=request.form["password"] , confirm_password=request.form["confirm_password"])# if email & pass types are correct , user will be navigated to upload page
        except:
            print("type error")
            return redirect(url_for("login"))
        with Session(engine) as db_session :
            query = select(User).where(User.username == register_login_data.username ) #    User.password == register_login_data.password)
            result = db_session.exec(query).first()
        if request.form["confirm_password"] == request.form["password"] :
            
            if result :
                #check if username exists
                byte_password = register_login_data.password.encode("utf-8")
                if bcrypt.checkpw(byte_password , result.password):  
                    # check if password is correct   
                    session["username"]  =  register_login_data.username
                    print("you logged in successfully 🎉")
                    return redirect(url_for("upload")) 
                else:
                    print("password is incorrect")
                    return redirect(url_for("login"))
            else :
                print("username is incorrect")
                return redirect(url_for("login"))
        else :
            print("confirm password doesnt match with password , try again ... ")
            return redirect(url_for("login"))



@app.route("/logout" , methods=["GET"])
def logout():
        session.pop("username")
        print("YOU LOGGED OUT ")    
        return redirect(url_for("main_page"))


@app.route("/upload" , methods=["GET" ,"POST"])
async def upload() :
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
                    img = cv2.imread(upload_path)
                    # final_image , age =  predictor(upload_path)
                    result = DeepFace.analyze(img_path = img, actions = ['age'] ,  enforce_detection=False, silent=True)
                    await asyncio.sleep(13)
                    age = result[0]['age']
                    
                    save_path = os.path.join("static/uploads/", user_image.filename)
                    cv2.imwrite(save_path, img)              
                    result = make_response(render_template("result.html" ,image_link= save_path ,  age=age ))
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



@app.route("/image_classification" , methods=["GET" , "POST"])
async def image_classification():
    if request.method == "GET" : 
        return make_response(render_template("classification_result.html"))
    
    elif request.method == "POST":
        input_image = request.files["image"]
        if input_image.filename == "" :
            return make_response(render_template("classification_result.html"))
        elif input_image and allowed_files(input_image.filename):
            path = os.path.join(app.config["UPLOAD_FOLDER"] , input_image.filename)
            input_image.save(path)
            path = str(path)
            print(str(path))
            saved_image = cv2.imread(path)

            model = YOLO('models/yolov8n-seg.pt')
            results = model.predict(path)
            result = results[0]
            print(result)                
            box = result.boxes[0]
            output = []
            for box in result.boxes:
                class_id = result.names[box.cls[0].item()]
                cords = box.xyxy[0].tolist()
                cords = [round(x) for x in cords]
                conf = round(box.conf[0].item(), 2)
                # output.append([cords, result.names[class_id], conf])
                print("Object type:", class_id)
                print("Coordinates:", cords)
                print("Probability:", conf)
                print(cords[0],cords[1],cords[2],cords[3])

            await asyncio.sleep(2)

            cv2.putText(img=saved_image , text=f"{class_id} : {conf}" , org=(cords[0],cords[1]-10) , fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.1, color=(100, 0, 250), thickness=2, lineType=cv2.LINE_AA)
            cv2.rectangle(saved_image, (cords[1], cords[0]), (cords[2], cords[3]), (100, 0, 250), 2)
            result_path = os.path.join("static/uploads/", "final_classified_image.jpg")
            cv2.imwrite( result_path , saved_image )
            return make_response(render_template("classification_result.html" , image_link=result_path))





# how to run
# bc our main file is app.py , so ther is no need to use ""app"" word in command
# flask run --debug
