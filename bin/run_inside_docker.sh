xhost +local:docker
sudo docker load -i ../wifi_positioning.tar.gz
sudo docker run -it --privileged --net=host -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY wifi-positioning-final
