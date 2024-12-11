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

docker run -p 7775:80 template-app-template-app
docker run -p 7777:80 template-app-template-app
docker exec -it template-app-template-app /bin/bash