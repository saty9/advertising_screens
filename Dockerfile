FROM python
RUN apt-get update && apt-get install -y nginx
RUN pip install uwsgi

WORKDIR /srv/ads
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY /media/* /srv/media/
COPY mock_deploy/settings.py /srv/ads/advertising/settings.py
COPY mock_deploy/api-endpoint.conf /etc/nginx/sites-enabled/api-endpoint.conf
RUN python manage.py collectstatic

CMD ["/bin/sh", "-c", "nginx && uwsgi --socket 0.0.0.0:8000 --enable-threads --module advertising.wsgi"]
