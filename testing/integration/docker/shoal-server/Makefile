build-image:
	sudo docker build -t shoal-server .

run:
	sudo docker run -d --name="shoal-server" shoal-server

connect:
	sudo docker exec -i -t shoal-server /bin/bash

stop:
	sudo docker stop shoal-server

clean:
	sudo docker rmi -f shoal-server
