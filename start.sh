#!/bin/bash
echo "Starting the application..."
sudo docker compose down
sudo docker compose up --build
echo "Application started successfully."