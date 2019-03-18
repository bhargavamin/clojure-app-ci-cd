FROM clojure:lein
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY build/newsfeed.jar /usr/src/app/
ENV APP_PORT=8001
CMD ["java", "-jar", "newsfeed.jar"]
EXPOSE 8001