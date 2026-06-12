#!/bin/bash
echo "Cleaning up sender files..."
rm -rf reciever.py
rm -rf receiver.DOCKERFILE
rm -rf docker-compose.receiver.yaml
rm -rf setup.reciever.sh
echo "Sender files cleaned up successfully."