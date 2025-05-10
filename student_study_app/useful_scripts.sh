cd ~/demohub/apps_bootcamp/team_074
chmod 777 *
colima start --cpu 4 --memory 8
docker login
docker network create demo-hub-network
docker network ls
docker-compose up -d

docker ps -a

docker stop <container id>
docker rm <container id>
docker rmi <image id>

docker login

docker run -p 7775:80 resume-app-resume-app
docker run -p 7777:80 resume-app-resume-app
docker exec -it resume-app /bin/bash
docker logs -f resume-app