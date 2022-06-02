FROM base_java:v1

WORKDIR /OneMedia

# to break cache
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache

COPY . .
COPY ./BUILD_DEPLOY/search/run_in_container.sh /OneMedia

RUN ["chmod", "+x", "run_in_container.sh"]
ENTRYPOINT ["./run_in_container.sh"]