#!/bin/bash
while read p; do
  echo $p
  if [[ $p == #* ]]; then
    echo "  -ignore"
done <symlinks.txt