# Docker :
- One Container per Services
- Volumes for data persistence
- One Network connected to all Services
- Docker compose specs
	- build
		- context
	- image
	- container_name
	- restart: unless-stopped
	- env_file / volumes / expose / ports / networks :
		- <element>
- Docker volumes:
	- volume:
		- driver: local
		- driver_opts:
			type :
			device :
			o: bind
- Dockerfile, add tini for signals handling.
- A Dockerfile per Containers
- A Dockerignore per Containers
