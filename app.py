import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import cv2.data
from flask import Flask , render_template , request, redirect,session , url_for , make_response
import cv2
from deepface import DeepFace
import asyncio

# from gevent.pywsgi import WSGIServer


app =Flask("face analysis")

# define some configs
app.config["UPLOAD_FOLDER"] = "static/uploads/" # folder which uploaded file will be saved in
app.config["ALLOWED_EXTENSIONS"] = {"png" , "jpg" , "jpeg"}
# app.config["FLASK_APP"] = "app.py"
# app.config["FLASK_ENV"]="development"

#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def auth(email , password):
    # if email == "k.jhnshid@gmail.com" and password == "1234" :
    #     return True
    # else :
    #     return False
    return True

def allowed_files(filename):
    return True




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
                    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)                
                    result = DeepFace.analyze(upload_path ,actions=["age" , "emotion", "gender" ] , enforce_detection=False)
                    
                    #await asyncio.sleep(11)
                    age = result[0]["age"]
                    emotion = result[0]["dominant_emotion"]
                    gender = result[0]["dominant_gender"]
                    #race = result[0]["dominant_race"]

                    save_path = os.path.join("static/uploads/", user_image.filename)
                    cv2.imwrite(save_path, image)
                    print(user_image.filename)
                    result = make_response(render_template("upload.html" ,image_link= save_path ,  age=age , emotion=emotion , gender=gender ))
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