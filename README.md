rebar
=====

Boot a rackspace install and install puppet using fabric.

Installation
------------

Clone this repo.

Install python dependencies

    pip install -r requirements.txt

Setup
------
Edit lib/datacenters.py with the relevant information. You can also change
the staring image in settings.py

Using
-----

To use run the `fab` command with subsequent commands.

### Examples

Create new server called webserver.mydomain.com and print the generated root
password to the console.

	fab DC_production system_bootstrap:webserver.mydomain.com

You can also add hosts to the *host.py* file to run commands from *rebar.py*

	fab host add_user:'myusername','mypassword'


TODO
----

* Automatically install modules to puppet master