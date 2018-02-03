#!/bin/bash

nohup firefly -c config.yml -b 0.0.0.0:80 > logs & disown
