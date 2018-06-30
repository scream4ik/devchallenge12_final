.PHONY: up down ps test logs

up:
	-@docker-compose up -d --build

down:
	-@docker-compose down

ps:
	-@docker-compose ps

test:
	-@docker-compose exec web pytest -s

# If the first argument is "logs"...
ifeq (logs,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "logs"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif
logs:
	-@docker-compose logs -f $(RUN_ARGS)
