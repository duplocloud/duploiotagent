FROM ubuntu:14.04
RUN apt-get update
RUN apt-get install --yes --no-install-recommends software-properties-common
RUN apt-get install --yes --no-install-recommends python-pip
RUN apt-get install --yes --no-install-recommends git
RUN apt-get install --yes --no-install-recommends curl
RUN pip install requests
RUN pip install boto3
RUN pip install docker
COPY . /duplodocker/duploiotagent
WORKDIR /agent
ENTRYPOINT ["/bin/bash", "-c", "/agent/native.agent.sh"]
