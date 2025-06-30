# =================================================
# Enhanced Makefile for Docker-based Development
# =================================================

# Configuration variables
BACKEND_ENV_FILE =  backend/.env
FRONTEND_ENV_FILE = frontend/.env
DOCKER_COMPOSE_CMD = docker compose

# Colors for better readability
CYAN = \033[0;36m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
RESET = \033[0m

# Define all phony targets (targets that don't produce a file with the target's name)
.PHONY: help setup up build down build-up clean prepare-env-files test frontend-test frontend-lint frontend-format

# Default target when just 'make' is executed
.DEFAULT_GOAL := help

# =================================================
# HELP SECTION
# =================================================
help:
	@echo "${CYAN}Docker Commands:${RESET}"
	@echo "  ${GREEN}make up${RESET}                    - Start containers in detached mode"
	@echo "  ${GREEN}make build${RESET}                 - Build containers"
	@echo "  ${GREEN}make down${RESET}                  - Stop and remove containers"
	@echo "  ${GREEN}make build-up${RESET}              - Build and start containers"
	@echo "  ${GREEN}make clean${RESET}                 - Clean up Docker resources"
	@echo ""
	@echo "${CYAN}Frontend Commands:${RESET}"
	@echo "  ${GREEN}make frontend-test${RESET}         - Run frontend tests"
	@echo "  ${GREEN}make frontend-lint${RESET}         - Lint frontend code"
	@echo "  ${GREEN}make frontend-format${RESET}       - Format frontend code"
	@echo ""
	@echo "${CYAN}Migration Commands:${RESET}"
	@echo "  ${GREEN}make generate-migration name=...${RESET} - Generate a new migration"
	@echo "  ${GREEN}make migrate-up-latest${RESET}     - Run migrations up to latest"
	@echo "  ${GREEN}make migrate-up n=...${RESET}      - Run n migrations up"
	@echo "  ${GREEN}make migrate-down-previous${RESET} - Revert last migration"
	@echo "  ${GREEN}make migrate-down n=...${RESET}    - Revert n migrations"
	@echo ""
	@echo "${CYAN}Testing Commands:${RESET}"
	@echo "  ${GREEN}make test${RESET}                   - Run all tests"
	@echo ""
	@echo "${CYAN}Setup Commands:${RESET}"
	@echo "  ${GREEN}make prepare-env-files${RESET}     - Create environment files (backend & frontend)"
	@echo "  ${GREEN}make setup${RESET}                 - Complete project setup"

# =================================================
# CONTAINER MANAGEMENT
# =================================================
up:
	@echo "${CYAN}Starting containers in detached mode...${RESET}"
	@${DOCKER_COMPOSE_CMD} up --detach

build:
	@echo "${CYAN}Building containers...${RESET}"
	@${DOCKER_COMPOSE_CMD} build

down:
	@echo "${CYAN}Stopping and removing containers...${RESET}"
	@${DOCKER_COMPOSE_CMD} down

build-up:
	@echo "${CYAN}Building and starting containers...${RESET}"
	@make build
	@make up

clean:
	@echo "${CYAN}Cleaning up Docker resources...${RESET}"
	@${DOCKER_COMPOSE_CMD} down --volumes --remove-orphans

# =================================================
# MIGRATIONS
# =================================================
generate-migration:
	@if [ -z "$(name)" ]; then \
		echo "${RED}Error: Missing migration name. Usage: make generate-migration name=your_migration_name${RESET}"; \
		exit 1; \
	fi
	@echo "${CYAN}Generating migration: $(name)${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm --user $$(id -u):$$(id -g) numismatist_migrations \
		sh -c "alembic revision --autogenerate -m '$(name)'"

migrate-up-latest:
	@echo "${CYAN}Running migrations up to latest version...${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm numismatist_migrations sh -c "alembic upgrade head"

migrate-up:
	@if [ -z "$(n)" ]; then \
		echo "${RED}Error: Missing number of migrations. Usage: make migrate-up n=number_of_migrations${RESET}"; \
		exit 1; \
	fi
	@echo "${CYAN}Running $(n) migrations up...${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm numismatist_migrations sh -c "alembic upgrade +$(n)"

migrate-down-previous:
	@echo "${CYAN}Reverting previous migration...${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm numismatist_migrations sh -c "alembic downgrade -1"

migrate-down:
	@if [ -z "$(n)" ]; then \
		echo "${RED}Error: Missing number of migrations. Usage: make migrate-down n=number_of_migrations${RESET}"; \
		exit 1; \
	fi
	@echo "${CYAN}Reverting $(n) migrations...${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm numismatist_migrations sh -c "alembic downgrade -$(n)"

prepare-env-files:
	@echo "${CYAN}Preparing environment files...${RESET}"
	@if [ ! -f ${BACKEND_ENV_FILE} ]; then \
		cp .env.backend.example ${BACKEND_ENV_FILE}; \
		echo "${GREEN}Environment file for backend prepared successfully${RESET}"; \
	else \
		echo "${YELLOW}Environment file for backend already exists, skipping${RESET}"; \
	fi
	@if [ ! -f ${FRONTEND_ENV_FILE} ]; then \
		cp .env.frontend.example ${FRONTEND_ENV_FILE}; \
		echo "${GREEN}Environment file for frontend prepared successfully${RESET}"; \
	else \
		echo "${YELLOW}Environment file for frontend already exists, skipping${RESET}"; \
	fi

setup: prepare-env-files build-up migrate-up-latest
	@echo "${GREEN}Setup complete!${RESET}"

# =================================================
# TESTING COMMANDS
# =================================================
test:
	@echo "${CYAN}Running all tests...${RESET}"
	@${DOCKER_COMPOSE_CMD} --profile tools run --rm numismatist_dev_tools sh -c "cd /app && python -m pytest tests/ -v"

# =================================================
# FRONTEND COMMANDS
# =================================================
frontend-test:
	@echo "${CYAN}Running frontend tests...${RESET}"
	@${DOCKER_COMPOSE_CMD} run --rm numismatist_frontend npm run test:unit

frontend-lint:
	@echo "${CYAN}Linting frontend code...${RESET}"
	@${DOCKER_COMPOSE_CMD} run --rm numismatist_frontend npm run lint

frontend-format:
	@echo "${CYAN}Formatting frontend code...${RESET}"
	@${DOCKER_COMPOSE_CMD} run --rm numismatist_frontend npm run format
