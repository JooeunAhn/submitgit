FROM ubuntu:precise
FROM python:3.5

maintainer joon

RUN apt-get update
RUN apt-get install -y build-essential git
RUN apt-get install -y python python-dev python-setuptools
RUN apt-get install -y nginx supervisor
RUN easy_install pip

RUN pip install uwsgi

RUN apt-get install -y python-software-properties software-properties-common
RUN apt-get update
RUN add-apt-repository -y ppa:nginx/stable

# install our code
ADD . /code/

ADD requirements.txt /code/

# RUN pip install on app requirements
RUN pip install -r /code/requirements.txt

# sort out permissions
RUN chown -R www-data:www-data /code

# setup nginx config
RUN ln -s /code/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /code/supervisor-app.conf /etc/supervisor/conf.d/

WORKDIR /code

EXPOSE 80 22
CMD ["supervisord", "-n"]