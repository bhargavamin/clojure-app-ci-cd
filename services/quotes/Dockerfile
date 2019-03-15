FROM clojure:lein
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN ls -la
COPY build/quotes.jar /usr/src/app/
ENV APP_PORT=8002
CMD ["echo", "$APP_PORT"]
CMD ["java", "-jar", "quotes.jar"]
EXPOSE 8002