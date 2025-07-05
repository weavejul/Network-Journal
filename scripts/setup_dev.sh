#!/bin/bash

# Network Journal Development Setup Script

set -e

echo "🚀 Setting up Network Journal development environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need it for the database."
    echo "   You can install it from https://docs.docker.com/get-docker/"
fi

echo "✅ Prerequisites check passed"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install
cd ..

# Setup backend
echo "🔧 Setting up backend..."
cd backend/api
pip install -r requirements.txt
cd ../..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
DEBUG=true

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

# AI Configuration (Add your API keys here)
OPENAI_API_KEY=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
ANTHROPIC_API_KEY=your-anthropic-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here

# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
MAX_TOKENS=4000
TEMPERATURE=0.1

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging Configuration
LOG_LEVEL=INFO

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
EOF
    echo "✅ Created .env file. Please update it with your API keys."
fi

# Create gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.dockerignore

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
EOF
    echo "✅ Created .gitignore"
fi

echo ""
echo "🎉 Setup complete! Here's what you can do next:"
echo ""
echo "1. Start the database:"
echo "   docker-compose up neo4j redis -d"
echo ""
echo "2. Start development servers:"
echo "   npm run dev:all"
echo ""
echo "3. Or start them separately:"
echo "   npm run dev:frontend  # Frontend on http://localhost:3000"
echo "   npm run dev:backend   # Backend on http://localhost:8000"
echo ""
echo "4. View the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Access Neo4j browser:"
echo "   http://localhost:7474"
echo ""
echo "📚 For more information, see the README.md file." 