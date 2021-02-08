#!/bin/bash


function tmp_file #name [where]
{
    local WHAT=$1
    local DIR=${2:="/tmp"}
    echo $(mktemp $DIR/$WHAT.XXXXXX)
}

