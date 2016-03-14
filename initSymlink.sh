#!/bin/bash
while read p; do
  if [[ $p == "#"* ]] || [[ $p == "" ]];
  then
    continue;
  fi
  ln -s $p

done <symlinks.txt
