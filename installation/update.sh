 #! /bin/bash
 cd ./debs
 dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
 dpkg -i *.deb
