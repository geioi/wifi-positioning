if [ -n "$1" ]; then
	sudo iw $1 interface add mon0 type monitor
	sudo ifconfig mon0 up
	echo "interface mon0 based on $1 is now running in monitor mode!"
else
	echo "Missing interface parameter! You can check the available interfaces by typing 'ipconfig'"
fi
