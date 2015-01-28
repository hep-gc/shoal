# Shoal Server v0.7.X README

##Services
**Shoal Server** provides two services that can be utilized by clients.

###RESTful API
Clients can use the Shoal Server RESTful API to retrieve a list of nearest squids. Assuming Shoal Server is running on `localhost` the following commands can be used:

- To get a list of the default 5 nearest verified squids use:
 - 'http:localhost/nearestverified'
- To retrieve a variable size of nearest verified squids you can use `http://localhost/nearestverified/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
 - `http://localhost/nearestverified/20`

- To get a list of the default 5 nearest squids use:
 - `http://localhost/nearest`
- To retrieve a variable size of nearest squids you can use `http://localhost/nearest/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
 - `http://localhost/nearest/20`
 
-To get a list of all squids stored in shoal use:
 'http://localhost/all'
 
###Optional Features
The new release of shoal has several new optional features
- Verification
 - The new verification feature is toggleable in the shoal_server configuration file
 - Shoal server will verify the squids advertised by shoal agents by checking their connectivity and attempting to download a common file from a repo on the proxy.
- Access Levels (requires GeoIP domain database**)
 - Shoal server will intelligently serve proxies to requesters based on Access Levels
 - Access Levels are configurable on the shoal-agents with 3 levels of access
  - Global: accessible from anywhere and will be served to any requester
  - Same Domain Only: accessible from anywhere but will only be served by requesters from the same domain (can still be verified)
  - No Outside Access: only accessible from inside the network due to firewall or other configuration, only served to requesters from same domain (cannot be verified)

**GeoIP2 Domain database will have to be manually placed in the proper directory default:
`/var/www/shoal/static/db/`

###WPAD
Shoal Server has a basic implementation of the [WPAD](http://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol) standard.

- To retrieve a WPAD file containing the 5 closest squids you can visit:
  - `http://localhost/wpad.dat`

##Installation
 _**Note**: Requires you have a working RabbitMQ AMQP Server, and Python 2.6+_
_Recommended to use a system wide install (sudo), but works in a virtualenv with tweaks_

_**Note**: Shoal static files will be located either at `~/shoal_server/` or `/var/shoal/` if sudo was used_

_**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if sudo was used_

###Recommended Method: Use yum

First install [EPEL](http://fedoraproject.org/wiki/EPEL)

    sudo yum install yum-conf-epel
    sudo yum update

Get the Shoal yum repository:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal.repo -o /etc/yum.repos.d/shoal.repo
   
Install the server:

    sudo rpm --import http://hepnetcanada.ca/pubkeys/igable.asc
    sudo yum install shoal-server
    
Configure the server and start it:

    vim /etc/shoal/shoal_server.conf
    service shoal-server start
    (it is recomended shoal server is run with apache see "Apache and Mod_WSGI" below)

###Using Pip

1. `pip install shoal-server`

2. Check settings in `shoal_server.conf` update as needed. Make sure RabbitMQ server is running.

4. Start `shoal-server`
  - _First run make take a few seconds to start as it needs to download the GeoLiteCity database (~12MB)._

5. Visit `http://localhost:8080`

###Using Git

1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-server/`
2.5 (optional) Make sure domain database is in /shoal-server/static/db/ prior to next step or it will not have the domain lookup functionality
3. `python setup.py install`
4. Check settings in `shoal_server.conf` update as needed. Make sure RabbitMQ server is running.
5. Start `shoal-server`
 - _First run make take a few seconds to start as it needs to download the GeoLiteCity database (~12MB)._

6. Visit `http://localhost:8080`

##Apache and Mod_WSGI

1. Use one of the following above methods to install Shoal Server.
 - Make sure the shoal_server package is in the **global** Python packages folder.

2. Adjust settings in `/etc/shoal/shoal_server.conf`
3. Make sure you have a working Apache installation with mod_wsgi.
    - sudo yum install httpd
    - sudo yum install mod_wsgi
4. Move Shoal folder to Apache readable location. `mv /var/shoal/ /var/www/`
 - _Ensure you also change `shoal_dir` in `shoal_server.conf` to point to new directory (`/var/www/shoal/` as per example)_

5. Include this bare minimum Apache config settings in a file within `/etc/httpd/conf.d/` or similiar location.

        WSGIDaemonProcess shoal user=www-data group=www-data threads=10 processes=1
        WSGIScriptAlias / /var/www/shoal/scripts/shoal_wsgi.py
        WSGIProcessGroup shoal

        Alias /static /var/www/shoal/static/

        AddType text/html .py 

        <Directory /var/www/shoal/>
            Order deny,allow
            Allow from all 
        </Directory>
 - Some values above may need to be adjusted depending on Linux Distro used.

6. Restart Apache.
7. Visit `http://localhost`

GEOIP DOMAIN LICENSE:
MaxMind GeoIP License version 1.7, July 21st, 2008

MAXMIND END-USER LICENSE AGREEMENT

By clicking on the words "I Agree" below, you agree that your use of the MaxMind GeoIP database products and services is subject to the terms and conditions set forth in this MaxMind End User License Agreement (this "Agreement").

MaxMind, Inc.("MaxMind") provides a line of database services and products that provide the geographic information and other data associated with specific Internet protocol addresses. These database services and products are referred to in this Agreement individually as the "GeoIP Database" and collectively as the "GeoIP Databases". The data available through the GeoIP Databases is referred to in this Agreement as the "GeoIP Data". Some products in the MaxMind GeoIP Line may include MaxMind's proprietary computer programs used to query the GeoIP Databases (the "GeoIP Programs"). The referenced GeoIP Databases and related services and products are accessible via the MaxMind website, www.maxmind.com (the "Site").

ADDITIONAL POLICIES.

The following policies are incorporated into this End User Agreement by reference and provide additional terms and conditions related to specific services and products provided by MaxMind:

minFraud Service Terms of Use

Each of these policies may be amended at any time and such amendments shall be binding and effective as indicated below in the section on Changes To The Agreement.

LIMITED GRANT OF RIGHTS.

In accordance with the terms of this Agreement, MaxMind hereby grants you a non-exclusive, non-transferable limited license to access and use the GeoIP Databases and GeoIP Data for your own internal Restricted Business purposes. Restricted Business purposes are limited to customizing website content, fraud prevention, geographic reporting, and similar business purposes. You agree to use the GeoIP Data and GeoIP Databases only in a manner that is consistent with applicable laws.

RESTRICTIONS ON USE.

Except as expressly permitted in this Agreement, you may not, nor may you permit others to:

(a) copy any portion of the GeoIP Databases except as reasonably required for using the GeoIP Database as permitted hereunder,

(b) allow anyone other than yourself or your employees to access the GeoIP Databases, or any portion thereof, without MaxMind's express written permission,

(c) use the GeoIP Databases to develop a database, infobase, online or similar database service, or other information resource in any media (print, electronic or otherwise, now existing or developed in the future) for sale to, distribution to, display to or use by others,

(d) create compilations or derivative works of the GeoIP Databases,

(e) use the GeoIP Databases in any fashion that may infringe any copyright, intellectual property right, contractual right, or proprietary or property right or interest held by MaxMind,

(f) store in a retrieval system accessible to the public, transfer, publish, distribute, display to others, broadcast, sell, or sublicense the GeoIP Databases, or any portion thereof,

(g) remove or obscure any copyright notice or other notice or terms of use contained in the GeoIP Databases,

(h) use the GeoIP Data to create or otherwise support the transmission of unsolicited, commercial email,

(i) remove, disable, avoid, circumvent, or defeat any functionality in the GeoIP Databases or GeoIP Programs designed to limit or control access to or use of the GeoIP Databases or GeoIP Data,

(j) use, copy or otherwise access any portion of the GeoIP Data for which you have not made payment to MaxMind. If for any reason, you access such GeoIP Data, these terms and conditions apply to your use of such data and you agree to pay all applicable charges, or

(k) copy, reverse engineer, decompile, disassemble, derive source code, modify or prepare derivative works of the GeoIP Programs.

OWNERSHIP AND INTELLECTUAL PROPERTY RIGHTS.

(a) Trade Secrets and Confidential Information. You acknowledge and agree that any and all confidential information and materials from which MaxMind derives actual or potential economic value constitutes MaxMind's confidential and proprietary trade secrets (collectively, "Trade Secrets"). You further acknowledge and agree that MaxMind's Trade Secrets include, but are not limited to, the GeoIP Databases, the GeoIP Data, and the technology used in the GeoIP Programs. You shall maintain any information learned about MaxMind's Trade Secrets as confidential and shall not disclose such information or permit such information to be disclosed to any person or entity. With respect to all such information, you shall exercise the same degree of care to protect MaxMind's Trade Secrets that you exercise with respect to protecting your own confidential information, and in no event less than reasonable care.

(b) Ownership. All intellectual property rights including copyrights, moral rights, trademarks, trade secrets, proprietary rights to the GeoIP Databases, GeoIP Data and GeoIP Programs are exclusively owned by MaxMind. You acknowledge and agree that you obtain no right, title or interest therein. You hereby assign to MaxMind all copyrights, intellectual property rights, and any other proprietary or property rights or interests in and to any work created in violation of this Agreement.

FEES.

MaxMind's current fee schedule for using the GeoIP Databases and related services is posted on the MaxMind website (url: http://www.maxmind.com). You are responsible for paying all fees associated with the use of the GEOIP Databases.

CHANGES TO THE AGREEMENT.

MaxMind may amend this Agreement at any time. Any such amendment(s) shall be binding and effective upon the earlier of (i) the date that is thirty (30) days after posting of the amended Agreement on MaxMind's web site, or (ii) the date that MaxMind provides notice to you of the amended Agreement pursuant to the notice provisions in this Agreement; except that changes to charges and payment terms may be made only upon 30 days' prior written notice to you. You may immediately terminate this Agreement upon notice to MaxMind if a change is unacceptable to you. Your continued use of the GeoIP Data, GeoIP Databases or GeoIP Programs following notice to you of a change shall constitute your acceptance of the change.

LIMITATION ON LIABILITY.

MAXMIND'S MAXIMUM TOTAL LIABILITY FOR ALL OCCURRENCES (IF ANY), TAKING PLACE DURING ANY TWELVE-MONTH PERIOD (OR A PORTION THEREOF, IF THIS AGREEMENT IS NOT IN EFFECT FOR TWELVE MONTHS), ARISING OUT OF OR IN ANY WAY RELATED TO THE AUTHORIZED OR UNAUTHORIZED ACTS OF MAXMIND'S EMPLOYEES OR MAXMIND'S PERFORMANCE OR NONPERFORMANCE OF THE SERVICES PROVIDED HEREIN, INCLUDING (BUT NOT LIMITED TO) ERRORS OF DESIGN OR ERRORS WHICH ARE DUE SOLELY TO MALFUNCTION OF MAXMIND-CONTROLLED MACHINES OR FAILURES OF MAXMIND OPERATORS, MAXMIND PROGRAMMERS OR MAXMIND-DEVELOPED PROGRAMS, SHALL BE LIMITED TO GENERAL MONEY DAMAGES IN AN AMOUNT NOT TO EXCEED THE TOTAL AMOUNT PAID BY YOU FOR SERVICES PROVIDED BY MAXMIND UNDER THIS AGREEMENT DURING SAID TWELVE-MONTH PERIOD (OR DURING SUCH SHORTER PERIOD THAT THIS AGREEMENT IS IN EFFECT). YOU AGREE THAT THE FOREGOING SHALL CONSTITUTE YOUR EXCLUSIVE REMEDY. YOU HEREBY RELEASE MAXMIND, ITS OFFICERS, EMPLOYEES AND AFFILIATES FROM ANY AND ALL OBLIGATIONS, LIABILITIES AND CLAIMS IN EXCESS OF THIS LIMITATION.

NO CONSEQUENTIAL DAMAGES.

UNDER NO CIRCUMSTANCES INCLUDING NEGLIGENCE SHALL MAXMIND OR ANY RELATED PARTY OR SUPPLIER BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES; OR FOR LOSS OF PROFITS, REVENUE, OR DATA; THAT ARE DIRECTLY OR INDIRECTLY RELATED TO THE USE OF, OR THE INABILITY TO ACCESS AND USE THE GEOIP DATABASES AND RELATED SERVICES, WHETHER IN AN ACTION IN CONTRACT, TORT, PRODUCT LIABILITY, STRICT LIABILITY, STATUTE OR OTHERWISE EVEN IF MAXMIND HAS BEEN ADVISED OF THE POSSIBILITY OF THOSE DAMAGES.

NO WARRANTIES.

THE GEOIP DATABASES, GEOIP DATA AND GEOIP PROGRAMS ARE FURNISHED ON AN "AS IS", AS-AVAILABLE BASIS. MAXMIND MAKES NO WARRANTY, EXPRESS OR IMPLIED, WITH RESPECT TO THE CAPABILITY OF THE GEOIP DATABASES, GEOIP DATA AND GEOIP PROGRAMS OR THE ACCURACY OR THE COMPLETENESS OF THE GEOIP DATA. ALL WARRANTIES OF ANY TYPE, EXPRESS OR IMPLIED, INCLUDING THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS ARE EXPRESSLY DISCLAIMED. MAXMIND DOES NOT WARRANT THAT THE SERVICES WILL MEET ANY PARTICULAR CRITERIA OF PERFORMANCE OR QUALITY, OR THAT THE SITE IS FREE OF OTHER HARMFUL COMPONENTS. NEVERTHELESS, MAXMIND SHALL MAKE COMMERCIALLY REASONABLE EFFORTS TO MAINTAIN THE SITE FREE OF VIRUSES AND MALICIOUS CODE.

GOVERNING LAW.

This Agreement shall be governed and interpreted pursuant to the laws of the Commonwealth of Massachusetts, applicable to contracts made and to be performed wholly in Massachusetts, without regard to principles of conflicts of laws. You specifically consent to personal jurisdiction in Massachusetts in connection with any dispute between you and MaxMind arising out of this Agreement or pertaining to the subject matter hereof. You agree that the exclusive venue for any dispute hereunder shall be in the state and federal courts in Boston, Massachusetts.

NOTICES

Notices given under this Agreement shall be in writing and sent by facsimile, e-mail, or by first class mail or equivalent. MaxMind shall direct notice to you at the facsimile number, e-mail address, or physical mailing address (collectively, "Address") you provided in the registration process. You shall direct notice to MaxMind at the following address:

MaxMind, Inc. PO Box 926 Boston, MA 02117-0926 Email: legal@maxmind.com Fax: (815) 301-8737

Either party may change its Address for notice at anytime by giving notice of the new Address as provided in this section.

COMPLETE AGREEMENT.

This Agreement represents the entire agreement between you and MaxMind with respect to the subject matter hereof and supersedes all previous representations, understandings or agreements, oral or written, between the parties regarding the subject matter hereof.

APPLICABLE LAWS.

You agree to use the GeoIP Data and GeoIP Databases only in a manner that is consistent with applicable laws.

ASSIGNMENT.

You may not assign your rights in this Agreement without MaxMind's prior written consent.

SEVERABILITY.

Should any provision of this Agreement be held void, invalid or inoperative, such decision shall not affect any other provision hereof, and the remainder of this Agreement shall be effective as though such void, invalid or inoperative provision had not been contained herein.

FAILURE TO ENFORCE.

The failure of MaxMind to enforce any provision of these terms and conditions shall not constitute or be construed as a waiver of such provision or of the right to enforce it at a later time.

FACSIMILES.

If you submit a document which includes your facsimile signature, MaxMind may treat the facsimile signature as an original of your signature.

CAPTIONS.

The section headings used herein, are for convenience only and shall have no force or effect upon the construction or interpretation of any provision hereof. 
