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

If things go wrong, this service can be somewhat hungry in terms of disk usage. You should check

```
journalctl --disk-usage
```

It is recommended that you 

```
journalctl --vacuum-size=50M # or other size
journalctl --vacuum-size=1d # or any other period
```

You can also choose to keep the sizes of logs small *permanently*. It's recommended that you use as script to do this (especially if you are running multiple Rpi). Assuming you have ssh access to the with `username` and `password`, and you can read `ip` (`df['ip']`) addresses from each of the raspberry pis in the network (df['computer_name']). This script assumes a pattern of `'raspberry'` and converts all to lower case, adjust as necessary.

```
def configure_journalctl(df, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    raspberries = df[df['computer_name'].str.lower().str.contains("raspberry", na=False)]
    print(f"found these raspberries ({len(raspberries.index)})")
    print(raspberries)
    
    for index, row in raspberries.iterrows():
        ip = row['ip']  # Assuming IP is stored in the YAML file
        try:
            print(f"Trying IP {ip}")
            ssh.connect(ip, username=username, password=password, timeout=10)
            # Get current disk usage of journalctl
            stdin, stdout, stderr = ssh.exec_command("journalctl --disk-usage")
            current_usage = stdout.read().decode().strip()
            print(f"Current journalctl disk usage on {row['computer_name']} ({ip}): {current_usage}")
            # Execute configuration commands
            commands = [
              "sudo sed -i '/SystemMaxUse=/c\\SystemMaxUse=50M' /etc/systemd/journald.conf",
              "sudo systemctl restart systemd-journald",
              "sudo journalctl --rotate",
              "sudo journalctl --vacuum-size=50M",
              "journalctl --disk-usage"  # Check disk usage again after changes
                    ]
            
            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                print(f"Executed on {row['computer_name']} ({ip}): {command}")
                print(stdout.read().decode() + stderr.read().decode())
            ssh.close()
        except Exception as e:
            print(f"Failed to connect or execute on {row['computer_name']} ({ip}): {e}")
```