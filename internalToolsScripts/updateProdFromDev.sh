#!/bin/bash
cd /robotics/services/InternalTools
git checkout master
git pull origin develop --no-edit
git push origin master
git checkout production
git pull origin master --no-edit
git push origin production
