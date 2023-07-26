#    go-binsize-viz, Go executable vizualisation
#    Copyright (C) 2018-2022 Raphael 'kena' Poss
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
FROM golang:1-alpine

# dockerizing https://github.com/knz/go-binsize-viz project

ENV USER=go-binsize-viz
ENV GROUP=go-binsize-viz

ENV HOME_DIRECTORY=/home/go-binsize-viz/
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

ADD . ${HOME_DIRECTORY}/

RUN chmod +x ${HOME_DIRECTORY}/go-binsize-viz.sh

WORKDIR ${HOME_DIRECTORY}/
USER go-binsize-viz

ENTRYPOINT [ "/home/go-binsize-viz/go-binsize-viz.sh" ]
