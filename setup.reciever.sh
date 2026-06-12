#!/bin/bash
echo "Cleaning up receiver files..."
rm -rf main.py
rm -rf main.DOCKERFILE
rm -rf init_db.sql
rm -rf init.sql
rm -rf nginx.conf
rm -rf setup.sender.sh
rm -rf docker-compose.yaml
mv docker-compose.receiver.yaml docker-compose.yaml
echo "Receiver files cleaned up successfully."