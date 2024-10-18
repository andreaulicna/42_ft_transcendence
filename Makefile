name = transcendence

all:
	@echo "Configuring ${name}\n"
	@bash ./tools/make_volume.sh
	@docker-compose -f ./docker-compose.yml up -d

build:
	@echo "Building ${name}\n"
	@bash ./tools/make_volume.sh
	@docker-compose -f ./docker-compose.yml build --no-cache
	@docker-compose -f ./docker-compose.yml up -d

stop:
	@echo "Stopping ${name}\n"
	@docker-compose -f ./docker-compose.yml down

re: clean all

clean: stop
	@echo "Cleaning ${name}\n"
	@docker system prune -a --force	# remove all unused images
	@IMAGES=$$(docker images -qa); if [ -n "$$IMAGES" ]; then docker rmi -f $$IMAGES; fi
	@CONTAINERS=$$(docker ps -qa); if [ -n "$$CONTAINERS" ]; then docker stop $$CONTAINERS; fi
	@docker system prune --all --force --volumes	# remove all (also used) images
	@docker network prune --force	# remove all networks
	@docker volume prune --force	# remove all connected partitions

fclean:
	@echo "Cleaning everything that's got anything to do with ${name}!\n"
	@CONTAINERS=$$(docker ps -qa); if [ -n "$$CONTAINERS" ]; then docker stop $$CONTAINERS; fi
	@IMAGES=$$(docker images -qa); if [ -n "$$IMAGES" ]; then docker rmi -f $$IMAGES; fi
	@docker system prune --all --force --volumes	# remove all (also used) images
	@docker network prune --force	# remove all networks
	@docker volume prune --force	# remove all connected partitions
	@sudo rm -rf ~/data

.PHONY: all build stop re clean fclean