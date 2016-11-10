#!/bin/bash


if [ $# -lt 2 ];then
    echo "usage: \n"$0" mode"
    exit -1;
elif [ "$1"x = "client"x ];then
    client
elif [ "$1"x = "cluster"x ];then
    cluster
else
    echo "fuck U?"
fi

cluster(){

}

client(){
    echo "please input the"
}