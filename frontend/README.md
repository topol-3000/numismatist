# Numismatist Frontend

A modern Vue.js 3 application for the Numismatist project, built with TypeScript, Vue Router, Pinia for state management, and Vite as the build tool.

## Features

- **Vue 3** with Composition API and `<script setup>`
- **TypeScript** for type safety
- **Vue Router** for client-side routing
- **Pinia** for state management
- **Vitest** for unit testing
- **Playwright** for end-to-end testing
- **ESLint** and **Prettier** for code quality
- **Docker** support for development and production

## Quick Start with Docker

The frontend is integrated into the main project's Docker setup. From the project root:

```sh
# Complete project setup
make setup
```

The frontend development server will be available at `http://localhost:5173`

## Environment Configuration

The frontend uses environment variables for configuration:

- **Template**: `.env.frontend.example` (in project root)
- **Active config**: `frontend/.env` (created by `make prepare-env-files`)
- **Key variables**:
  - `VITE_API_BASE_URL` - Backend API URL
  - `VITE_APP_TITLE` - Application title
  - `VITE_APP_VERSION` - Application version

## Development Commands

Frontend-specific tasks are available through the project's Makefile:

```sh
# From the project root
make frontend-test        # Run unit tests
make frontend-lint        # Lint code
make frontend-format      # Format code

# Standard Docker commands work for frontend too:
make up                   # Start frontend (and other services)
make down                 # Stop frontend (and other services)
make build                # Build frontend (and other containers)
```

## Local Development

### Prerequisites
- Node.js 22+ 
- npm

### Setup

```sh
npm install
```

### Development Server

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
