#!/bin/bash

function downloadBlob {
    echo downloadBlob $1

    mkdir -p ${1:0:2}
    cd $_

    wget -q -nc $domain/${dic}.git/objects/${1:0:2}/${1:2}

    cd ..
}

function parseTree {
    echo parseTree $1

    downloadBlob $1

    while read line
    do
        type=$(echo $line | awk '{print $2}')
        hash=$(echo $line | awk '{print $3}')

        [ "$type" = "tree" ] && parseTree $hash || downloadBlob $hash
    done < <(git cat-file -p $1)
}

function parseCommit {
    echo parseCommit $1

    downloadBlob $1

    tree=$(git cat-file -p $1| sed -n '1p' | awk '{print $2}')
    parseTree $tree

    parent=$(git cat-file -p $1 | sed -n '2p' | awk '{print $2}')

    [ ${#parent} -eq 40 ] && parseCommit $parent
}

[ -z $1 ] && echo -e "missing target url\n\n\
Usage: scrabble <url>\n\
Example: scrabble http://example.com/\n\n\
You need make sure target url had .git folder"\
&& exit

domain=$1
dic=$2
localdic=${dic}_bak.git
lastHash=$(curl -s $domain/$dic.git/refs/heads/master)
echo ${lastHash}
git init --bare ${localdic}
cd ${localdic}/objects

parseCommit ${lastHash}

cd ../../

echo $lastHash > ${localdic}/refs/heads/master
