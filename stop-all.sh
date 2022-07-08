#!/bin/bash

echo "Close all processes marked by 'grabber-bbb-mustansir'"
ps aux | grep "grabber-bbb-mustansir" | awk '{print $2}' | xargs -r kill -9

echo "Done"
