#
# This Source Code Form is subject to the terms of the Mozilla Public License, v.
# 2.0 with a Healthcare Disclaimer.
# A copy of the Mozilla Public License, v. 2.0 with the Healthcare Disclaimer can
# be found under the top level directory, named LICENSE.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# http://mozilla.org/MPL/2.0/.
# If a copy of the Healthcare Disclaimer was not distributed with this file, You
# can obtain one at the project website https://github.com/igia.
#
# Copyright (C) 2021-2022 Persistent Systems, Inc.
#
FROM python:3.7.7-buster

RUN python3 -m venv .venv
 
RUN . .venv/bin/activate

RUN python3 -m pip install --upgrade cython

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
 
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
 
RUN apt-get update
RUN apt-get -y install apt-utils
 
RUN env ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN env ACCEPT_EULA=Y apt-get -y install mssql-tools
RUN apt-get -y install unixodbc-dev 
RUN apt-get -y install python-dev graphviz libgraphviz-dev pkg-config

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

CMD ["bash"]
