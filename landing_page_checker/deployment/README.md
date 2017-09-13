# Provisioning/deployment Notes

These are approximate notes. In everything that follows replace SITENAME with the domain.

## Nginx install

```
$ sudo apt-get install nginx
$ sudo systemctl start nginx
```

## Configure domains

Point staging and prod domains to the server in question

## Setup Let's Encrypt

* Install `certbot`:

```
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot
```

* Make a folder to store the challenge:

```
cd /var/www/
mkdir letsencrypt
chgrp www-data letsencrypt
```

* Edit and put `letsencrypt-SITENAME.conf` in `/etc/letsencrypt/configs`

* Generate cert:

```
sudo certbot --config /etc/letsencrypt/configs/letsencrypt-SITENAME.conf certonly
```

## Setup nginx

* Edit `nginx.template.conf`
* Put it in `/etc/nginx/sites-available/SITENAME`
* Create a symlink to `/etc/nginx/sites-enabled/SITENAME`

## Configure `systemd` to start/reload `gunicorn`

* Edit `gunicorn-systemd.template.service`
* Put it in `/etc/systemd/system/SITENAME.service`
