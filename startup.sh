#!/bin/bash

uwsgi_threads=""
bucket_name=""
iperf_port=29999

while test -n "$1" ; do
    case "$1" in
        --uwsgi-threads)
            uwsgi_threads="$2"
            shift 2
            ;;
        --bucket_name)
            bucket_name="$2"
            shift 2
            ;;
        --iperf_port)
            iperf_port=$2
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

config="/etc/uwsgi.ini"
if test $uwsgi_threads != "" ; then
    sed -i "/^threads/i threads = $uwsgi_threads" $config
    sed -i '/^threads/{x;/./p;d}' $config
fi

config="/data/NodeAgent/config/base.ini"
if test $bucket_name != "" ; then
    sed -i "/bucket_name/i bucket_name = $bucket_name" $config
    sed -i '/bucket_name/{x;/./p;d}' $config
fi

while true
do
    # check iperf
    ret=$(ps -ef |grep iperf | grep -v grep)
    if test -z "$ret";then
        echo "$(date) $(cat /etc/hostname) iperf start"
        iperf -s -p $iperf_port -f m &
    fi

    # check uwsgi
    ret=$(ps -ef |grep /usr/local/bin/uwsgi | grep -v grep)
    if test -z "$ret";then
        echo "$(date) $(cat /etc/hostname) uwsgi start"
        /usr/local/bin/uwsgi /etc/uwsgi.ini &
    fi

    sleep 3
done
