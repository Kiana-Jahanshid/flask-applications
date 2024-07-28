import os    
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
os.environ["YOLO_CONFIG_DIR"] = tempfile.mkdtemp()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from quart import Quart , render_template , request, redirect,session as quart_session , url_for , flash 
import cv2
from pydantic import BaseModel
import bcrypt
# from deepface import DeepFace
from databasefile import fetch_user , add_user_to_db , fetch_all_users , relative_time_from_string , add_comment_to_db , add_comment_ToFaceAnalysisDB ,   fetch_comments , fetch_faceanalysis_comments , fetch_all_blogposts , add_NewPost_to_DB , read_a_post
from PIL import Image
from io import BytesIO 
import base64
import glob 
from image_classification import YOLOv8
from face_analysis import FaceAnalysis 
from datetime import datetime
import json 

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
    joined_time : str

class LoginModel(BaseModel):
    username : str
    password : str

class RegisterComments(BaseModel): 
    comment : str
    username : str
    user_id : int 
    

class RegisterPost(BaseModel):
    ...


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
            register_data = RegisterModel(username=(await request.form)["username"] ,password=(await request.form)['password'] , city=(await request.form)["city"]  ,country=(await request.form)["country"] , first_name=(await request.form)["firstname"] , last_name=(await request.form)["lastname"] , email=(await request.form)["email"] , age=(await request.form)["age"] , confirm_password=(await request.form)["confirm_password"] , joined_time=str(datetime.now()))#validating attributes type
            print((await request.form)["username"])
        except:
            await flash("Type Error! One of your input was wrong" , "danger")
            return redirect(url_for("register"))
        if register_data.confirm_password == register_data.password :
            user  = fetch_user(register_data.username)
            if not user :
                password_byte = register_data.password.encode("utf-8")
                hashed_password = bcrypt.hashpw(password_byte , bcrypt.gensalt())
                hashed_password = hashed_password.decode("utf-8")
                add_user_to_db(register_data.username ,  hashed_password , register_data.city , register_data.country , register_data.first_name , register_data.last_name , register_data.email , register_data.age , register_data.joined_time)
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
            register_login_data = LoginModel(username=(await request.form)["username"] , password=(await request.form)["password"])# if email & pass types are correct , user will be navigated to upload page
        except:
            await flash("Type error! ,One of your inputs has a wrong datatype" , "danger")
            return redirect(url_for("login"))
        user  = fetch_user(register_login_data.username)
        if user :
            byte_password = register_login_data.password.encode("utf-8")
            if bcrypt.checkpw(byte_password , bytes( user.password , "utf-8" ) ): # user.password (for postgres)
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



@app.route("/logout" , methods=["GET"])
async def logout():
        quart_session.pop("user_id")
        await flash("YOU LOGGED OUT " , "success")    
        return redirect(url_for("main_page"))


@app.route("/upload" , methods=["GET" ,"POST"])
async def upload() :
    if quart_session.get("user_id"):

        if request.method == "GET" :
            return await render_template("upload.html" )
        elif request.method == "POST" :
            user_image = (await request.files)["image"] # name of input tag was image in login file # uploaded file is in  ( request.files() )
            postfix =str( user_image.filename.rsplit('.', 1)[1].lower() )
            prefix =str( user_image.filename.rsplit('.', 1)[0].lower() )
            if user_image.filename == "" :
                return await render_template("upload.html")
            else :
                if user_image  : 
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"] , user_image.filename)
                    await user_image.save(upload_path)

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

                    face_analysis = FaceAnalysis("models/det_10g.onnx", "models/genderage.onnx")
                    output_image, gender, age = face_analysis.detect_age_gender(readed_image)

                    result_path_face = os.path.join("static/uploads/", f"{prefix}y.{postfix}")
                    cv2.imwrite( result_path_face , output_image )
                    all_comments = fetch_faceanalysis_comments()
                    result = await render_template("result.html" ,image_link= result_path_face , all_comments=all_comments)
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
            all_comments= fetch_comments()
            return await render_template("classification_result.html" , all_comments=all_comments)
        elif request.method == "POST":
            input_image = (await request.files)["image"]
            postfix =str( input_image.filename.rsplit('.', 1)[1].lower() )
            prefix =str( input_image.filename.rsplit('.', 1)[0].lower() )
            if input_image.filename == "" :
                return await render_template("classification_result.html")
            elif input_image :
                path = os.path.join(app.config["UPLOAD_FOLDER"] , input_image.filename)
                await input_image.save(path)
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

                object_detector = YOLOv8("models/yolov8n.onnx", confidence_threshold=0.5, iou_threshold=0.5)
                output_image, output_labels = object_detector(readed_image)
                result_path = os.path.join("static/uploads/", f"{prefix}z.{postfix}")
                cv2.imwrite( result_path , output_image )
                all_comments= fetch_comments()
                return await render_template("classification_result.html" , image_link=result_path, all_comments=all_comments )
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



@app.route("/admin" , methods=["GET", "POST"])
async def pannel_admin():
    if quart_session.get("user_id") : #or quart_session.get("role") != "Admin":
        all_users , user_count = fetch_all_users()
        for user in all_users :
            joined_time = str(user.joined_time)
            parsed_time = datetime.strptime(joined_time, '%Y-%m-%d %H:%M:%S.%f')
            formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
            user.joined_time = relative_time_from_string(formatted_time)  

        ClassificationComments = fetch_comments()
        FaceAnalysisComments = fetch_faceanalysis_comments()
        posts = fetch_all_blogposts()
        return await render_template("admin.html" , username= quart_session.get("username") , users=all_users , user_count=user_count , ClassificationComments=ClassificationComments , FaceAnalysisComments=FaceAnalysisComments , posts=posts)
    else : 
        await flash("You have to login ⛔" , "info")
        return redirect(url_for("login"))



@app.route("/add_comment" , methods=["POST"])
async def comment(): 
    if quart_session.get("user_id"):
        comment = (await request.form)["text"] 
        comment_model = RegisterComments(comment=comment , username=quart_session.get("username") , user_id=quart_session.get("user_id"))
        comment_model.comment = comment[3:-4] #  tag <p> removed bc it didn't let font style to be shown 
        add_comment_to_db(comment=comment_model.comment , username=comment_model.username , user_id=comment_model.user_id)
        return redirect(url_for("image_classification"))
    else :
        await flash("You have to login ⛔" , "info")
        return redirect(url_for("login"))


@app.route("/add_comment_faceanalysis" , methods=["POST"])
async def comment_faceanalysis(): 
    if quart_session.get("user_id"):
        comment = (await request.form)["text"]
        comment_model = RegisterComments(comment=comment , username=quart_session.get("username") , user_id=quart_session.get("user_id"))
        comment_model.comment = comment[3:-4] #  tag <p> removed bc it didn't let font style to be shown 
        add_comment_ToFaceAnalysisDB(comment=comment_model.comment , username=comment_model.username , user_id=comment_model.user_id)
        return redirect(url_for("upload"))
    else :
        await flash("You have to login ⛔" , "info")
        return redirect(url_for("login"))
    


@app.route("/api" , methods=["GET","POST"])
async def user_count():
    _ , user_count = fetch_all_users()
    json_data = f'{{"users":{{"count": {user_count} }}}}'
    j = json.dumps(json_data, indent=2)     
    j = json.loads(j) 
    return await render_template("count.html" , json=j )



@app.route("/blog" , methods=["GET", "POST"])
async def blogpost():
    posts = fetch_all_blogposts()
    for post in posts :
        released_time = str(post.time_stamp)
        parsed_time = datetime.strptime(released_time, '%Y-%m-%d %H:%M:%S.%f')
        formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
        post.time_stamp = relative_time_from_string(formatted_time) 
    return await render_template("blog.html" , posts=posts)


@app.route("/add_post" , methods=["GET","POST"])
async def posts(): 
    if quart_session.get("user_id"):
        post_title = (await request.form)["post_title"]
        post_content = (await request.form)["post_content"] # ❌ for this field, should assign ((name="")) in form input ❌
        # post_content = post_content[3:-4] 
        add_NewPost_to_DB(title=post_title , content=post_content , author=quart_session.get("username") , user_id=quart_session.get("user_id"))
        return redirect(url_for("blogpost"))
    else :
        await flash("You have to login ⛔" , "info")
        return redirect(url_for("login"))
    

@app.route("/post_detail/<string:title>" )
async def post_detail(title):
    post = read_a_post(title=title)
    released_time = str(post.time_stamp)
    parsed_time = datetime.strptime(released_time, '%Y-%m-%d %H:%M:%S.%f')
    formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
    post.time_stamp = relative_time_from_string(formatted_time)
    return await render_template("post_detail.html" , post=post)


if __name__ == "__main__":
    app.run(debug=True , host="0.0.0.0" ,port="5000")





# how to run
# bc our main file is app.py , so ther is no need to use ""app"" word in command
# flask run --debug

# now : 
# quart --app app run


# in docker-compose : 
# will be run at http://127.0.0.1:8080