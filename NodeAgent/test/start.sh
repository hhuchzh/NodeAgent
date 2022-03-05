#!/bin/bash
while true
do
    http_code=`curl -o /dev/null -s -w %{http_code} "http://127.0.0.1:4999/api/v1/pot/timeout/cloudui-99"`
    if [ $http_code -eq 201 ]
    then
        echo "timeout, exit"
        break
    else
        echo "$http_code"
        sleep 20
    fi
done
    
