export DOCKER_HOST=unix:///run/docker.sock

docker build -t flask-docker-app .
sudo systemctl start docker
sudo systemctl status docker

docker container ls -a
docker image ls
docker run -d -p 5000:5000 --name model flask-docker-app
docker logs model
docker container rm -f model
docker ps
docker stop <container_id>
docker stop <container_name>
docker ps -a

<!-- --privileged بيخلي الكونتينر عنده access كامل للهاردوير (بس استخدميه بحذر). -->
docker run --privileged --device=/dev/video0 -p 5000:5000 your_image_name
