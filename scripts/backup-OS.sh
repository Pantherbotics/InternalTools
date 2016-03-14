#!/bin/bash
touch /var/log/rsyncLocalBackup
echo "Backup started at: $(/bin/date)" | tee /var/log/rsyncLocalBackup
rsync -aAXhvP --stats --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found","/smb/*"} /* /media/OS-BACKUP | tee /var/log/rsyncLocalBackup
rsync -aAXhv --stats  /mnt/stg/OS-BACKUP/ /mnt/stg/OS-BACKUP_OLD
rsync -aAXhvP --stats --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found","/smb/*"} /* /mnt/stg/OS-BACKUP

echo "Backup finished at: $(/bin/date)" | tee /var/log/rsyncLocalBackup

