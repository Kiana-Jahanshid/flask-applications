FROM python

WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install opencv-python-headless
# RUN apt-get install -y --no-install-recommends \ libgl1 \ libglib2.0-0
# RUN apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy app code and set working directory
COPY . .
# EXPOSE 5000
# ENV FLASK_APP=app.py
# Run
# CMD ["quart", "run", "--port=5000", "--host=0.0.0.0"]
# CMD [ "flask", "run" ,"--host=0.0.0.0", "--port=5000"]
CMD ["hypercorn", "app:app" ]