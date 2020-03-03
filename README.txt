
cronsched.py is a crontab scheduler that can be used to set a crontab to run for specific users at specific times

attack_scan.py is a scanner and attack automater using nmap that currently only works automating nikto scans but can be used over a large number of hosts and ports

web_get.py is my interpretation of the wget command using only the socket, sys, and os libraries that I created for my Computer Networks class (ACO330)

The backdoor.py and backdoor_client.py are both programs I created following a lengthy video tutorial

backdoor.py starts a server on a Linux machine that waits for the backdoor_client to connect to it, so that the backdoor can send commands to the client

backdoor_client.py is a malicious program that when someone is tricked into running it on a Windows machine, tries to connect to the backdoor.py so that commands can be sent to it
