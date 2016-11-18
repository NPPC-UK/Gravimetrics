"""This file is made to install crontabs automatically for Gravimetrics """

from crontab import CronTab

# Run as this user; generally this will be pi
gravi_cron = CronTab(user='nathan')

# this is the command to be ran with this cronjob
cmd = 'python3 /gravi_control/gravi.py'
comment = 'Gravimetrics main script'

# Create the cronjob to run at 9 and 21 hours
cron_job = gravi_cron.new(cmd, comment)
cron_job.hour.on(9, 21)

# Commit the job
gravi_cron.write()

# Show our changes
print(gravi_cron.render())
