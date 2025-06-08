# =================================================
# Enhanced Makefile for Docker-based Development
# =================================================

# Configuration variables
BACKEND_ENV_FILE =  backend/.env
DOCKER_COMPOSE_CMD = docker compose

# Colors for better readability
CYAN = \033[0;36m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
RESET = \033[0m

# Define all phony targets (targets that don't produce a file with the target's name)
.PHONY: help setup up build down build-up clean prepare-env-files

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
	@echo "${CYAN}Setup Commands:${RESET}"
	@echo "  ${GREEN}make prepare-env-files${RESET}     - Create environment files"
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

prepare-env-files:
	@echo "${CYAN}Preparing environment files...${RESET}"
	@if [ ! -f src/.env ]; then \
		cp .env.backend.example ${BACKEND_ENV_FILE}; \
		echo "${GREEN}Environment file for backend prepared successfully${RESET}"; \
	else \
		echo "${YELLOW}Environment file for backend already exists, skipping${RESET}"; \
	fi

setup: prepare-env-files build-up
	@echo "${GREEN}Setup complete!${RESET}"