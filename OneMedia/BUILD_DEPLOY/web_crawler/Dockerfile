FROM base_python:v1

WORKDIR /OneMedia

RUN apt -y update
RUN apt-get -y install tor
RUN echo "ControlPort 9051" >> /etc/tor/torrc
RUN echo "HashedControlPassword $(tor --quiet --hash-password pass)" >> /etc/tor/torrc
RUN /etc/init.d/tor restart

EXPOSE 9050
EXPOSE 9051

COPY . .
COPY ./BUILD_DEPLOY/web_crawler/run_in_container.sh /OneMedia

# add working directory to source roots
ENV PYTHONPATH="${PYTHONPATH}:/OneMedia"

RUN ["chmod", "+x", "run_in_container.sh"]
ENTRYPOINT ["./run_in_container.sh"]