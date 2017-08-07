FROM node:6.10.3-alpine

LABEL maintainer="Freedom of the Press Foundation"
LABEL description="Sass-lint designed for one-off usage - compat. w/ grsec"

# Tooling needed to address issues when running under grsec
RUN apk add paxctl --no-cache &&\
        paxctl -cm /usr/local/bin/node

RUN npm install sass-lint -g && npm cache clean

ENTRYPOINT ["/usr/local/bin/sass-lint", "-v"]
