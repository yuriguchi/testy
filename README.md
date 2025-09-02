# TestY TMS

___
TestY is an open source project developed by KNS Group LLC (YADRO) as an alternative to other test managements
systems.  
Project is lightweight and uses django-rest-framework as core for its backend.

### Docker production deployment from scratch

___

1. Go to `{project_root}/nginx` directory and execute `make_ssl.sh` to create self-signed ssl certificates.
2. Create .env file, you can find example with comments in repository *.env.template*  
   **Possible problems for env file**:
    1. everything is served via nginx so keep it in mind when setting VITE_APP_API_ROOT.
    2. VITE_APP_API_ROOT should be *http://\<host\>* **NO TRAILING SLASH AT THE END**
    3. Pay attention to http/https in your VITE_APP_API_ROOT
3. `docker-compose up` starts production version of TestY
    1. DB runs on port 5435
    2. TestY backend runs on port 8000
    3. TestY frontend runs on port 3000
    4. Nginx ports are 80 for dev and 80 with 443 on production environment
    5. Plugins page runs on backend only and doesn't have native ui.
4. For production deployment frontend will be served as static and not launched via npm.

## WARNING FOR PRODUCTION USAGE

**UPGRADE WARNING, upgrade to 2.0.4 only tested from version 1.3.4, upgrade from earlier versions at your own risk, 
before any upgrade make a backup of your current data**

1. For real production deployment we highly recommend using working signed SSL certificates, you can set path to them
   inside .env files `SSL_CERT_KEY_PATH` for key file and `SSL_CERT_PATH` cert file accordingly.
2. Change `VOLUMES_PATH` for some other path than root, because every hard redeployment or local repository deletion
   will delete your volumes information
3. Do not use default settings for database
4. Do not leave superuser creds as it is.
5. To set servername in nginx config we provide `HOST_NAME` env variable, by default it is `_`
6. To start with `docker compose up` not as root user you need to add your user id as UID environment variable,   
by default we are using user with id 0 (which is root or default user)

## Contribution and development deployment

___

1. Docker deployment is almost the same as a production one but omit step with creating certificates
   as they are not used in development nginx config.
2. Run `docker-compose -f docker-compose-dev.yml up`
3. UI is not served as static in development mode.
4. Django settings are set to development mode, so you will see drf api view and detailed django Internal server errors.

### For contribution rules and running applications without docker check out [CONTRIBUTING.md](https://gitlab-pub.yadro.com/testy/testy/-/blob/main/CONTRIBUTING.md)

## Known issues

`entrypoint.sh` has linux line separators, so it breaks on Windows machines.