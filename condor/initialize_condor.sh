#!/bin/bash

voms-proxy-init --rfc --voms cms -valid 192:00

OUTPUT=`voms-proxy-info`

voms_proxy_file="temp"

for word in $OUTPUT
do
    if [[ "$word" == *"tmp"* ]]; then
        voms_proxy_file="$word"
        cp $voms_proxy_file $PWD
    fi
done

