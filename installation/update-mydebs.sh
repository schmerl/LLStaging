#! /bin/bash
cd /vagrant/debs
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz