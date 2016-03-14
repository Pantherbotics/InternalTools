cred=$(</robotics/bridgeCred.txt)
ssh -t robotics@10.42.0.1 "echo -e '$cred\n' | sudo -S nmcli c up id CVUSD"

