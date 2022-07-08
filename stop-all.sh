#!/bin/bash

ps aux | grep "grabber-bbb-mustansir" | awk '{print $2}' | xargs -r kill -9

