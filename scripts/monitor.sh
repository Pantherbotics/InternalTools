SESSION="monitor"
tmux kill-session -t $SESSION
tmux new-session -d -s $SESSION


tmux split-window -vp 52
tmux send-keys "multitail -cS smbaudit /var/log/samba-audit.log -cS gitSync /robotics/logs/gitSync" C-m

tmux select-pane -t 0
tmux send-keys "while ! /robotics/scripts/countdown.sh ; do : ; done" C-m
tmux split-window -hp 50
tmux send-keys "tty-clock -tscC 7" C-m
tmux select-pane -t 0
tmux split-window -vp 77
tmux send-keys "speedometer -r enp0s25 -t enp0s25 -s" C-m
tmux select-pane -t 2
tmux split-window -vp 77
tmux send-keys "python /robotics/scripts/display.py" C-m
tmux attach-session -t $SESSION
