FROM nginx:latest


COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./conf.d /etc/nginx/conf.d


EXPOSE 1111

CMD ["nginx", "-g", "daemon off;"]
