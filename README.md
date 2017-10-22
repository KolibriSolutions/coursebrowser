# osiristue
## Description
This repo contains the source code for the unofficial interface of TU/e Osiris, hosted in production at [https://osiristue.nl/](https://osiristue.nl/). It utilizes the Unofficial Osrisis API, created by the same authors. More information on the API can be found in its repo. This system is build in the [Django framework](https://www.djangoproject.com/).

It aims to provide a usefull interface in which students can easily filter and browse courses to help with making a choice in them. It uses the Unoficial Osiris API to fetch all courses from a requested faculty and caches the tables for 12 hours. The interface code is shared with the code base of the [Master Marketplace](https://master.ele.tue.nl/)

## Usage
Install python and the requirements using pip. Consult the django docs for information on how to deploy the system. It needs redis and postgresql as external dependencies.

## Acknowledgments
The API was developed for usage with the [Master Marketplace](https://master.ele.tue.nl/), created for the ELE department of the TU/e. This Unofficial Interface has no official endorsement of the TU/e whatsoever. Development and support done by Kolibri Solutions. For questions or inquiries contact info@kolibrisolutions.nl.

All rights reserved. All product names, logos, and brands are property of their respective owners.  Use of these names, logos, and brands does not imply endorsement.
