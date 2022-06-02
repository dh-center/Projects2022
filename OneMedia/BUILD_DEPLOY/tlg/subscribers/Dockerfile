FROM base_python:v1

WORKDIR /OneMedia

COPY . .
COPY ./BUILD_DEPLOY/tlg/subscribers/run_in_container.sh /OneMedia

# add working directory to source roots
ENV PYTHONPATH="${PYTHONPATH}:/OneMedia"

RUN ["chmod", "+x", "run_in_container.sh"]
ENTRYPOINT ["./run_in_container.sh"]