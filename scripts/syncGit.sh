#!/bin/sh
cred=$(</robotics/gitCred.txt)
if ! ping -q -c 1 -W 1 8.8.8.8 >/dev/null; then
    #printf  "$(date)[NETWORK] error: network is offline! Resetting...\n"  >> /robotics/logs/gitSync
    bash /robotics/scripts/resetWifi.sh
    exit
fi
cd /robotics/git
for D in $(find /robotics/git/ -mindepth 1 -maxdepth 1 -type d) ; do
    cd $D
    if [ -f "no-github-sync" ];then
        echo "IGNORE $D"
        continue 
    fi
    exists=`git show-ref refs/heads/master`
    if ! [[ $(git show-ref refs/heads/master) ]] && test `find "git-daemon-export-ok" -mmin +4320`; then
        echo 'Repository is older than 3 days and is blank. DELETING PERMANENTLY' >> /robotics/logs/gitSync 
        cd ../
        mv $D /robotics/oldGit/$D
        N=${D/\/*\//};
        curl -u @cred -X "DELETE" https://api.github.com/repos/PantherboticsOrg/${N/.*/}; 
    else
        OUTF=$((git fetch hub refs/heads/*:refs/heads/*) 2>&1)
        OUTP=$((git push --all hub) 2>&1)

        if ! [[ $OUTF == "" ]]; then
            printf  "$(date) %-40s" [$D]  >> /robotics/logs/gitSync
            echo -e "$OUTF" | tr '\n' '\n          ' >> /robotics/logs/gitSync
        fi

        if ! [[ $OUTP == *"Everything up-to-date"* ]]; then
            printf  "$(date) %-40s" [$D]  >> /robotics/logs/gitSync
            echo -e "$OUTP" | tr '\n' '\n          ' >> /robotics/logs/gitSync
        fi
    fi
done
