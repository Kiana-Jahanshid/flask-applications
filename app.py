import os    
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
os.environ["YOLO_CONFIG_DIR"] = tempfile.mkdtemp()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from quart import Quart , render_template , request, redirect,session as quart_session , url_for , flash
import cv2
from pydantic import BaseModel
from ultralytics import YOLO
import bcrypt
from deepface import DeepFace
from databasefile import fetch_user , add_user_to_db 
from PIL import Image
from io import BytesIO 
import base64
import asyncio
import glob 

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


app =Quart("face analysis")
app.config["UPLOAD_FOLDER"] = "static/uploads/" 
app.config["ALLOWED_EXTENSIONS"] = {"png" , "jpg" , "jpeg"}
app.secret_key = "my_secret"


@app.route("/" , methods=["GET"])
async def main_page():
    return await render_template("index.html")


@app.route("/register" , methods=["GET","POST"])
async def register():
    if request.method == "GET" :
        return await render_template("register.html")
    elif request.method == "POST" :
        try:
            register_data = RegisterModel(username=(await request.form)["username"] ,password=(await request.form)['password'] , city=(await request.form)["city"]  ,country=(await request.form)["country"] , first_name=(await request.form)["firstname"] , last_name=(await request.form)["lastname"] , email=(await request.form)["email"] , age=(await request.form)["age"] , confirm_password=(await request.form)["confirm_password"])#validating attributes type
            print((await request.form)["username"])
        except:
            await flash("Type Error! One of your input was wrong" , "danger")
            return redirect(url_for("register"))
        if register_data.confirm_password == register_data.password :
            user  = fetch_user(register_data.username)
            if not user :
                password_byte = register_data.password.encode("utf-8")
                hashed_password = bcrypt.hashpw(password_byte , bcrypt.gensalt())
                add_user_to_db(register_data.username ,  hashed_password , register_data.city , register_data.country , register_data.first_name , register_data.last_name , register_data.email , register_data.age)
                await flash("Your SignUp compleated successfully 🎉" , "success") 
                return  redirect(url_for("login")) 
            else:
                await flash("This username is already taken ❌,Choose another one" , "danger")
                return  redirect(url_for("register"))
        else :
            await flash("Confirm-password doesn't match with password ,Try again..." , "warning")
            return  redirect(url_for("register"))



@app.route("/login" , methods=["GET" , "POST"]) 
async def login():
    if request.method == "GET" :
        return await render_template("login.html")
    elif request.method == "POST" : 
        try :            
            register_login_data = LoginModel(username=(await request.form)["username"] , password=(await request.form)["password"] , confirm_password=(await request.form)["confirm_password"])# if email & pass types are correct , user will be navigated to upload page
        except:
            await flash("Type error! ,One of your inputs has a wrong datatype" , "danger")
            return await redirect(url_for("login"))
        user  = fetch_user(register_login_data.username)

        if (await request.form)["confirm_password"] == (await request.form)["password"] :
            if user :
                byte_password = register_login_data.password.encode("utf-8")
                if bcrypt.checkpw(byte_password , user.password):  
                    quart_session["username"]  =  register_login_data.username
                    quart_session["user_id"] = user.id
                    await flash("You logged in successfully 🎉" , "success")
                    return redirect(url_for("main_page")) 
                else:
                    await flash("Password is incorrect ❌" , "danger")
                    return redirect(url_for("login"))
            else :
                await flash("Username is incorrect ❌" , "danger")
                return redirect(url_for("login"))
        else :
            await flash("Confirm-password doesn't match with password ,Try again...", "warning")
            return redirect(url_for("login"))


@app.route("/logout" , methods=["GET"])
async def logout():
        quart_session.pop("user_id")
        await flash("YOU LOGGED OUT " , "success")    
        return redirect(url_for("main_page"))


@app.route("/upload" , methods=["GET" ,"POST"])
async def upload() :
    if quart_session.get("user_id"):

        if request.method == "GET" :
            return await render_template("upload.html")
        elif request.method == "POST" :
            user_image = (await request.files)["image"] # name of input tag was image in login file # uploaded file is in  ( request.files() )
            postfix =str( user_image.filename.rsplit('.', 1)[1].lower() )
            prefix =str( user_image.filename.rsplit('.', 1)[0].lower() )
            if user_image.filename == "" :
                return await render_template("upload.html")
            else :
                if user_image  : 
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"] , user_image.filename)
                    user_image.save(upload_path)

                    files = glob.glob('static/uploads/*')
                    for f in files:
                        os.remove(f)

                    img = Image.open(user_image.stream)
                    with BytesIO() as buf:
                        if postfix == "jpg" :
                            postfix = "jpeg"
                        img.save(buf, postfix)
                        image_bytes = buf.getvalue()
                    encoded_string = base64.b64encode(image_bytes).decode()
                    imgdata = base64.b64decode(encoded_string)
                    with open(f"static/uploads/face.{postfix}", 'wb') as f:
                        f.write(imgdata)
                    readed_image = cv2.imread(f"static/uploads/face.{postfix}")

                    result = DeepFace.analyze(img_path = readed_image , actions = ['age'] ,  enforce_detection=False, silent=True)
                    age = result[0]['age']

                    result_path_face = os.path.join("static/uploads/", f"{prefix}x.{postfix}")
                    cv2.imwrite( result_path_face , readed_image )
                    result = await render_template("result.html" ,image_link= result_path_face ,  age=age )
                    return result
    else :
        await flash("First you have to login to use applications ⛔" , "info")
        return redirect(url_for("login"))


@app.route("/bmr" , methods=["GET" , "POST"])
async def bmr_calc():
    if quart_session.get("user_id"):

        if request.method == "GET" :
            return await render_template("bmr.html")
        else :
            age = (await request.form)["age"]
            weight = (await request.form)["weight"]
            height = (await request.form)["height"]
            gender =  (await request.form)["gender"]
            print(age , weight , height , gender)
            if gender == "female" or gender == "Female" :
                bmr_result = (10*float(weight)) + (6.25*float(height)) - (5*float(age)) - 161
            elif gender == "male" or gender == "Male": 
                bmr_result = (10*float(weight)) + (6.25*float(height)) - (5*float(age)) + 5

            return await render_template("bmr.html" , bmr_result=bmr_result)
    else :
        await flash("First you have to login to use applications ⛔" , "info")
        return redirect(url_for("login"))


@app.route("/image_classification" , methods=["GET" , "POST"])
async def image_classification():
    if quart_session.get("user_id"):
        if request.method == "GET" : 
            return await render_template("classification_result.html")
        elif request.method == "POST":
            input_image = (await request.files)["image"]
            postfix =str( input_image.filename.rsplit('.', 1)[1].lower() )
            prefix =str( input_image.filename.rsplit('.', 1)[0].lower() )
            if input_image.filename == "" :
                return await render_template("classification_result.html")
            elif input_image :
                path = os.path.join(app.config["UPLOAD_FOLDER"] , input_image.filename)
                input_image.save(path)
                print(path)

                files = glob.glob('static/uploads/*')
                print(len(files))
                for f in files:
                    os.remove(f)

                img = Image.open(input_image.stream)
                with BytesIO() as buf:
                    if postfix == "jpg" :
                        postfix = "jpeg"
                    img.save(buf, postfix)
                    image_bytes = buf.getvalue()
                encoded_string = base64.b64encode(image_bytes).decode()
                imgdata = base64.b64decode(encoded_string)
                with open(f"static/uploads/upload.{postfix}", 'wb') as f:
                    f.write(imgdata)
                readed_image = cv2.imread(f"static/uploads/upload.{postfix}")

                model = YOLO('models/yolov8n-seg.pt')
                results = model.predict(readed_image)
                result = results[0]
                print(result)                
                box = result.boxes[0]
                for box in result.boxes:
                    class_id = result.names[box.cls[0].item()]
                    cords = box.xyxy[0].tolist()
                    cords = [round(x) for x in cords]
                    conf = round(box.conf[0].item(), 2)
                    print("Object type:", class_id)
                    print("Coordinates:", cords)
                    print("Probability:", conf)
                    print(cords[0],cords[1],cords[2],cords[3])

                cv2.putText(img=readed_image , text=f"{class_id} : {conf}" , org=(cords[0],cords[1]+80) , fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.2, color=(100, 0, 250), thickness=2, lineType=cv2.LINE_AA)
                cv2.rectangle(readed_image, (cords[1], cords[0]), (cords[2], cords[3]), (100, 0, 250), 2)
                result_path = os.path.join("static/uploads/", f"{prefix}z.{postfix}")
                cv2.imwrite( result_path , readed_image )
                await asyncio.sleep(2)
                return await render_template("classification_result.html" , image_link=result_path)
    else :
        await flash("First you have to login to use applications ⛔" , "info")
        return redirect(url_for("login"))



@app.route("/mind_reader" , methods=["GET" , "POST"])
async def mind_reader():
    if quart_session.get("user_id"):
        if request.method == "GET" : 
            return await render_template("mind_reader.html")
        elif request.method == "POST":
            selected_number = (await request.form)["selected_number"] #selected_number should assign in <input name="selected_number"> in html file
            result =  await render_template("result_mindreader.html" , selected_number=selected_number)
            return result
    else :
        await flash("First, you have to login to use applications ⛔" , "info")
        return redirect(url_for("login"))


@app.route("/pose_detection" , methods=["GET"])
async def pose_detection():
    if quart_session.get("user_id"):
            return await render_template("pose_detection.html")
    else : 
        await flash("First, you have to login to use applications ⛔" , "info")
        return redirect(url_for("login"))



# how to run
# bc our main file is app.py , so ther is no need to use ""app"" word in command
# flask run --debug

# now : 
# quart --app app run