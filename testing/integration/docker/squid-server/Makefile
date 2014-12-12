
build-image:
	sudo docker build -t squid-server .

run:
	sudo docker run --rm -d --name="squid-server" --link shoal-server:shoal-server squid-server

connect:
	sudo docker exec -i -t squid-server /bin/bash

stop:
	sudo docker stop squid-server

clean:
	sudo docker rmi -f squid-server



