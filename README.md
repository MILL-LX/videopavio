# videopavio
**Double Raspberry recording and streaming system.**  

One raspberry runs a python socket.io server, and the necessary sensors or buttons.  
The other(s) raspberry(s) act as recorder(s), running a client socket.io that waits for orders and runs a simple bash script to record and rsync the files back to the server.  
The idea is to have a server connected to a screen, showing a mix of the previously recorded videoloops and/or its internal camera feed depending on sensor state.  
The remote recorder(s) wait(s) for socket.io messages and when prompted records and sends the files back to the server.  
The latest file will then get mixed with the latest mix, creating a composition, using an overlay effect.  

## server role:
`sudo cp extras/videopavio_server.service /lib/systemd/system/`  
`sudo cp extras/videopavio_sensors.service /lib/systemd/system/`

## recorder role
`sudo cp extras/videopavio_recorder.service /lib/systemd/system/`

## both roles - activate the needed services
`sudo chmod 644 /lib/systemd/system/videopavio*`  
`sudo systemctl daemon-reload`  
`sudo systemctl enable videopavio_server.service`  
`sudo systemctl start videopavio_server.service`  
`sudo systemctl enable videopavio_sensors.service`  
`sudo systemctl start videopavio_sensors.service`  
`sudo systemctl enable videopavio_recorder.service`  
`sudo systemctl start videopavio_recorder.service`  
`sudo systemctl status videopavio_recorder.service`  
