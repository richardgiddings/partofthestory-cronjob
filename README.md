## README

A script that runs a Python file. This is to be used with the partofthestory application to unassign story parts if they have not been completed within 3 days of them being started. This stops stories from becoming stuck and enables someone else to pickup the story. The intention is to run the script on a scheduled basis as part of a cronjob.

Example run:
```
./run.sh
```

Note that environment variables are needed for the database connection parameters.