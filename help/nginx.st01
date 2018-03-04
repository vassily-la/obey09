# NGINX CONFIG
server {
  listen 80;
  server_name st01.vassily.pro;

  location /static {
    alias /home/vldo/sites/st01.vassily.pro/static;
  }

  location / {
    proxy_pass http://unix:/tmp/st01.vassily.pro.socket;
    proxy_set_header Host $host;
  }
}
