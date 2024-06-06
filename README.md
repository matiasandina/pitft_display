# pitft_display
Repository to control displays using Adafruit Mini PiTFT (https://www.adafruit.com/product/4393)

## Install

This software was tested under python 3.10.
Please create a virtual environmnet

```
conda create -n pitft_env python==3.10 pip
conda activate pitft_env
pip install -r requirements.txt
```

## Scripts

### Stat Monitor

```
(pitft_env) ~/pitft_display $ python3 monitor_stats.py
```

## Running at boot

If you want scripts in this repository to run in the background, follow the instructions below.

> [!IMPORTANT]  
> Run `which python` in order to get the proper execution path

> [!TIP]
> The steps below are detailed for the stat monitor using a python instance under `/home/pi/miniforge3/envs/pitft_env/bin/python` and a script located at `/home/pi/pitft_display/monitor_stats.py`, modify for your use if changing the script to run.

Using this following configuration file:

```
[Unit]
Description=Display service to run a stat monitor using pitft display
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/pi/miniforge3/envs/pitft_env/bin/python /home/pi/pitft_display/monitor_stats.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

```

1. Save the Configuration:

    1. Open a terminal.
    1. Use a text editor (like nano or vim) to create a new service file:

    ```
    sudo nano /etc/systemd/system/pitft_monitor_stats.service
    ```
    1. Copy and paste the modified service configuration above into the editor.
    1. Save and close the editor (CTRL+X, Y, Enter for nano).
1. Enable the Service:

```
sudo systemctl enable pitft_monitor_stats

```
1. Start the Service:

```
sudo systemctl start pitft_monitor_stats

```

1. Check the Service Status (or visually inspect the monitor):

```
sudo systemctl status pitft_monitor_stats
```
1. Try rebooting and checking if it executes properly or you get error logs

```
sudo journalctl -u pitft_monitor_stats

```
