#!/bin/bash
# Connects to the PostgreSQL database inside the container
docker-compose exec db psql -U postgres -d discord_bot_db
