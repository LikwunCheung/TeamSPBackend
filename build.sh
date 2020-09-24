#!/bin/sh

docker build --build-arg https_proxy=http://proxy.unimelb.edu.au:8000 --build-arg http_proxy=http://proxy.unimelb.edu.au:8000 -t sp90013/backend:latest .