# https://hub.docker.com/r/insanejflow/docker-django/
# https://github.com/JooeunAhn/docker-django
FROM mathpresso/docker-stella:python35

maintainer joon

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