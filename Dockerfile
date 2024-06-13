FROM python
WORKDIR /
# Expose port you want your app on
EXPOSE 5000

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy app code and set working directory
COPY . .


# Run
ENTRYPOINT ["flask", "run", "--port=5000", "--host=0.0.0.0"]

