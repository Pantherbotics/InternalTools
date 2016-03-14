#!/bin/bash
while read p; do
  if [[ $p == "#"* ]] || ! [[ $p == "/"* ]];
  then
    continue;
  fi
  echo $p

done <symlinks.txt