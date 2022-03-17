FROM clojure:lein
RUN apt-get update && apt-get install -y \
    python3 \
    curl

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY build/* /usr/src/app/
COPY front-end/public/serve.py /usr/src/app/
RUN tar -xvzf *.tgz -C .
