# Course Browser
## Description
This repo contains the source code for the Course Browser website, hosted in production at [https://coursebrowser.nl/](https://coursebrowser.nl/). It utilizes a scraper to gather course information. The scraper lives in OsirisAPI.py. This system is build in the [Django framework](https://www.djangoproject.com/).

It aims to provide a usefull interface in which students can easily filter and browse courses to help with making a choice in them. It uses the scraper to fetch all courses from a requested faculty and caches the tables for one month.

## Usage
Install python and the requirements using pip. Consult the django and django channels docs for information on how to deploy the system. It needs redis and postgresql as external dependencies.

### Disclaimer
The Course Browser system has no official endorsement of any university whatsoever. Development and support done by Kolibri Solutions. For questions or inquiries contact info@kolibrisolutions.nl.

All rights reserved. All product names, logos, and brands are property of their respective owners.  Use of these names, logos, and brands does not imply endorsement.
