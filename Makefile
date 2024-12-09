name = transcendence

all:
	@echo "Configuring ${name}\n"
	@bash ./tools/make_volume.sh
	@docker compose -f ./docker-compose.yml up -d

build:
	@echo "Building ${name}\n"
	@bash ./tools/make_volume.sh
	@docker compose -f ./docker-compose.yml build
	@docker compose -f ./docker-compose.yml up -d

stop:
	@echo "Stopping ${name}\n"
	@docker compose -f ./docker-compose.yml down

restart:
	@echo "Stopping ${name}\n"
	@docker compose -f ./docker-compose.yml restart

reset:
	@echo "Resetting ${name}\n"
	@docker compose -f ./docker-compose.yml down
	@docker compose -f ./docker-compose.yml up -d

re: clean all

down:
	@echo "Disabling ${name}\n"
	@docker compose -f ./docker-compose.yml down

clean: stop
	@echo "Cleaning ${name}\n"
	@docker system prune -a --force	# remove all unused images
	@CONTAINERS=$$(docker ps -qa); if [ -n "$$CONTAINERS" ]; then docker stop $$CONTAINERS; fi
	@IMAGES=$$(docker images -qa); if [ -n "$$IMAGES" ]; then docker rmi -f $$IMAGES; fi
	@docker system prune --all --force --volumes
	@docker network prune --force
	@docker volume prune --force
	
fclean: clean
	@VOLUMES=$$(docker volume ls -q); if [ -n "$$VOLUMES" ]; then docker volume rm $$VOLUMES; fi
	
.PHONY: all build stop re clean fclean