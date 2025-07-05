# Network Journal

My personal system for mapping, understanding, and leveraging professional
relationships!

## Architecture Overview

This project follows a three-tier architecture:

- **Frontend**: React + TypeScript SPA with a couple visualization libraries (for now- Cytoscape.js, D3.js, vis-network)
- **Backend**: FastAPI microservices with Neo4j graph database
- **AI Layer (WIP)**: LangChain(?)-powered services for double-checking and updating info

## Project Structure

```txt
network-journal/
├── frontend/                 # React + TypeScript application
├── backend/                  # FastAPI microservices
│   ├── api/                 # Main API gateway
│   ├── graph_service/       # Neo4j database service
│   └── ai_service/          # LangChain AI services
├── shared/                  # Shared types and utilities
├── docker/                  # Docker configurations
├── docs/                    # Documentation
└── scripts/                 # Development and deployment scripts
```

## Development Phases

- [x] **Phase 1**: Basic CRUD operations
- [x] **Phase 2**: Interactive network graph
- [ ] **Phase 3**: AI-powered note processing
- [ ] **Phase 4**: Agent cross-referencing

## Current Status

### **Completed? Features** (Subject to updates)
- [x] **Complete Backend API**: CRUD operations for People, Companies, Interactions, Topics, Events, and Locations Nodes
- [x] **Graph Database**: Neo4j integration with basic relationship modeling
- [x] **Network Visualization**: Visualization libraries (Cytoscape.js, D3.js, vis-network)
- [x] **React Frontend**: TypeScript, TailwindCSS, Radix UI components
- [x] **Testing**: Backend tests implemented
- [x] **Docker**: Full containerization

### **In Progress**

- [ ] AI note processing
- [ ] Make the backend API less annoying to work with
- [ ] Dynamic relationship handling
- [ ] Graph analytics
- [ ] UI/UX improvements

## Quick Start

```bash
# Install all dependencies (frontend + backend)
npm run install:all

# Start dev servers
npm run dev:all          # Run both frontend and backend
npm run dev:frontend     # Frontend only
npm run dev:backend      # Backend only

# Run tests
npm test                 # Run all tests
npm run test:frontend    # Frontend tests only
npm run test:backend     # Backend tests only

# Docker setup
npm run docker:build     # Build all containers
npm run docker:up        # Start all services
npm run docker:down      # Stop all services
```

## API Endpoints

The backend provides a REST API with the following endpoints:

- **People**: `/api/v1/people/` - CRUD operations, relationships, search
- **Companies**: `/api/v1/companies/` - CRUD operations, employee relationships
- **Interactions**: `/api/v1/interactions/` - Communication tracking, person linking
- **Topics**: `/api/v1/topics/` - Interest/skill management, popularity tracking
- **Events**: `/api/v1/events/` - Event management, attendance tracking
- **Locations**: `/api/v1/locations/` - Geographic data, popular locations
- **Graph**: `/api/v1/graph/` - Network data for visualization

All endpoints should support search, pagination, and relationship management. See backend API documentation for more details.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, TailwindCSS
- **Visualization**: Cytoscape.js, D3.js, vis-network, react-force-graph-2d
- **UI Components**: Radix UI, Shadcn UI, Framer Motion
- **State Management**: TanStack Query, React Hook Form, Zod
- **Backend**: FastAPI, Neo4j, Pydantic
- **AI**: OpenAI API (for now)
- **Deployment**: Docker, Vercel, Google Cloud Run
