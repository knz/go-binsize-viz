FROM golang:alpine3.9

# dockerizing https://github.com/knz/go-binsize-viz project

ENV USER=go-binsize-viz
ENV GROUP=go-binsize-viz

ENV HOME_DIRECTORY=/home/go-binsize-viz/
ENV BIN_DIRECTORY=/home/go-binsize-viz/bin
ENV LOG_DIRECTORY=/home/go-binsize-viz/template
ENV LIB_DIRECTORY=/home/go-binsize-viz/lib
ENV LANG C.UTF-8


RUN apk add --no-cache binutils bash python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache


RUN addgroup -g 1000 -S ${GROUP} && \
    adduser -u 1000 -S ${USER} -G ${GROUP}

RUN install -d -D -o ${USER} -g ${GROUP} ${HOME_DIRECTORY}/bin \
    ${HOME_DIRECTORY}/lib \
    ${HOME_DIRECTORY}/templates


ADD tab2pydic.py ${HOME_DIRECTORY}/lib
ADD simplify.py ${HOME_DIRECTORY}/lib
ADD app3.js ${HOME_DIRECTORY}/templates/app3.js
ADD js ${HOME_DIRECTORY}/templates/js
ADD treemap* ${HOME_DIRECTORY}/templates/
ADD go-binsize-viz.sh ${HOME_DIRECTORY}/bin/

RUN chmod +x ${HOME_DIRECTORY}/bin/go-binsize-viz.sh 

WORKDIR ${HOME_DIRECTORY}/
USER go-binsize-viz

ENTRYPOINT [ "/home/go-binsize-viz/bin/go-binsize-viz.sh" ]
