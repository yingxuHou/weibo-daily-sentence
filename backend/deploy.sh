#!/bin/bash

echo "Deploying Weibo Daily Sentence Backend..."

# Pull latest code
git pull origin main

# Stop existing containers
docker-compose down

# Build and start containers
docker-compose up -d --build

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check status
docker-compose ps

echo "Deployment completed!"
echo "API: http://your-server-ip:8000"
echo "API Docs: http://your-server-ip:8000/docs"
