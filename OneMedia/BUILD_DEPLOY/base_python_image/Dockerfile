FROM python:3.9-buster

WORKDIR /OneMedia

COPY requirements.txt .
RUN pip install -r requirements.txt
# add working directory to source roots
ENV PYTHONPATH="${PYTHONPATH}:/OneMedia"