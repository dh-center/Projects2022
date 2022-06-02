FROM base_java:v1

WORKDIR /OneMedia

ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
COPY . .
COPY ./BUILD_DEPLOY/ui/run_in_container.sh /OneMedia
COPY ./BUILD_DEPLOY/ui/build_jar.sh /OneMedia

RUN ["chmod", "+x", "run_in_container.sh"]
ENTRYPOINT ["./run_in_container.sh"]