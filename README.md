# Weather-logs-merger
This script merges the experiment logs with weather logs. Currently setup for Yarragadee but could be used for any of the other stations.

To run the script type in 
<code> python yg_wx_logs.py </code>

The script will prompt the user for
  * Experiment name,
  * Date of the experiment,
  * Start time,
  * End time.

With the given information, the script will

  * Download the required mets files containing the weather data using sftp,
  * Download the log file from pcfyg,
  * Merge the log from pcfs with the downloaded weather data,
  * Backup the original log on pcfsyg with a ''_original2.log'',
  * Copy the modified log back to the pcfsyg.

Once all that is done you can run the flogit script to transfer that log to the IVS servers. As usual please eyeball the log to make sure the script has done the right thing.
