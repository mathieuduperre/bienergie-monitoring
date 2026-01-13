# bienergie-monitoring
python script to monitor hydro-quebec bienergie light and send a state to a home assistant webhook. 


Usage:

install a raspberry pi (i.e. raspberry pi zero W)
use a PC817 coupler (from aliexpress) to connect the 2 wires from the hydro-quebec bi-energie light. connect that coupler to your raspberry pi on the 3.3v, ground, and a gpio of your choice. i'm using GPIO3 (pin 5). 
create a webhook in your home assistant

copy the script in your raspberry pi. edit the script to set your gpio, your webhook url
test your script (python3 binergy.py), make sure you can see the state change in your webhook through home assistant configuration (settings->helpers)

create a cron job (every minute in my case)
* * * * * /usr/bin/python3 /home/raspberry/binergy.py >> /home/raspberry/binergy.log 2>&1

voila. 
