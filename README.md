# funds-filtering
Built to automatize a daily manipulation between Generali Investments, our clients, and our partners.
- Imports a file containing financial data.
- Filters it on a scope of portfolio (scopeCustodian.csv)
- Sends it to a remote server through a SFTP connection
- Sends a mail alert if the script fails

3 parameters can be edited when running the command line :
- environment (UAT, PROD)
- name of the custodian
- country code

Scope of portfolios and mailing list can also be manually edited
