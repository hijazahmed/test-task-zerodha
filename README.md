# Zerodha Test Task

This repository contains code for zerodha's test task. The web app downloads bhavcopy zip from [BSE India](http://www.bseindia.com/markets/equity/EQReports/BhavCopyDebt.aspx?expandable=3) (every hour), parses it and shows top 10 gainers and loosers of the day. It has a search functionality built in to search for any company by name. Redis is used to store the data.

[Heroku Link](https://zerodha-rohan.herokuapp.com/)