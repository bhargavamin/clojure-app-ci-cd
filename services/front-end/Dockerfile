FROM clojure:lein
RUN apt-get update && apt-get install -y \
    python3
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY build/front-end.jar /usr/src/app/
COPY front-end/public /usr/src/app/

# Environment variables
ENV APP_PORT=8080 
ENV NEWSFEED_SERVICE_URL="http://test-infra-alb-1651004352.eu-west-1.elb.amazonaws.com/api/newsfeed"
ENV STATIC_URL="http://localhost:8000"
ENV QUOTE_SERVICE_URL="http://test-infra-alb-1651004352.eu-west-1.elb.amazonaws.com/api/quote"
ENV NEWSFEED_SERVICE_TOKEN="T1&eWbYXNWG1w1^YGKDPxAWJ@^et^&kX"
CMD ["python", "public/serve.py"]
CMD ["java", "-jar", "front-end.jar"]
EXPOSE 8080
EXPOSE 8000