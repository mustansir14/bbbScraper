#!/bin/bash

echo "Close all python marked by 'grabber-bbb-mustansir'"
ps aux | grep "grabber-bbb-mustansir" | grep "python" | awk '{print $2}' | xargs -r kill -9

echo "Close all chromedriver marked by 'grabber-bbb-mustansir'"
ps -ef | grep "grabber-bbb-mustansir" | grep "chrome" | awk '{print $3}' | xargs -r kill -9

echo "Close all chrome marked by 'grabber-bbb-mustansir'"
ps -ef | grep "grabber-bbb-mustansir" | grep "chrome" | awk '{print $2}' | xargs -r kill -9

echo "Done"
