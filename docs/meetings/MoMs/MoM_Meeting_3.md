## Overview
- Date : 08/03/2026.
- Start time : 10 AM.
- Launch break : 12 PM - 13h30 PM.
- End time : 15h30 PM.
- Location : Cantina, 42, Perpignan, France
## Attendance :
- [x] @nifromon
- [x] @juduchar
- [x] @cgregoir
- [x] @shanwang
## Agenda Items :
- Try to create a project base on docker from which we can test the chosen technologies of the project.
- Familiarize with the chosen technologies, verify that they are adapted for the project.
- Research modules, technologies based vocabulary and terms of the project.
- Research techniques we will have to use for the project.
## Notes :
### Norm :

#### Docker :
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

#### Structure :
- One Directory per modules || functionalities || services
- Each Directory / File must have a name adapted to it's content.
- Tree :
	- src/, core/, main/
	- assets/
	- docker/
	- docs/
		- meetings/
		- architecture.md
		- api.md
		- cpi.md
		- setup.md
		- security.md
	- tests/
	- Makefile
	- Readme.md
	- docker-compose
	- .gitignore

#### Documentation :
- Each Function must have a commentary above to describe it, explain how it works, and it's purpose.
- Each File must have a header that describe the content of the file, its purpose and  the functions involved.
- Each Directory :
	- Include mirror directory in docs/ which have a compilation of README.md files that explain how the module / service / functionality :
		- How did you approach it.
		- How did you solve it.
		- How did it go (bugs, problems, issues etc ...)
		- How it works.
		- How does it include itself in the project (purpose, dependancies etc ...)..
- Each README.md file must be written the Markdown format with a clear structure.

#### Github :
- Tree :
	- main
	- test
	- One branch / members
- Commit Convention : 
	- https://www.conventionalcommits.org/en/v1.0.0/
	- https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13
- Each personal push must be done in our own branches
- Each main push must be done with the group present or with a pull request.

### Base :

A Base project is being developped on which we could start the development of all other modules.

## Action Items :
- Basic Nginx by @cgregoir
- Baic PostGreSQL by @shanwang
- Basic ModSecurity WAF by @nifromon
- Basic File management by @juduchar
- Basic Tailwind CSS setup by @cgregoir (opt after Nginx)


