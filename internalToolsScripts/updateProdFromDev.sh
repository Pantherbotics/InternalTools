#!/bin/bash
cd /robotics/services/InternalTools
git checkout master
git pull origin develop --no-edit
git checkout production 
git pull origin master --no-edit
