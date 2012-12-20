FAQ
===

Q: When creating an image, MIC shows "Error <creator>: URLGrabber error: http://www.example.com/latest/repos/oss/ia32/packages/repodata/repomd.xml"

A: Perhaps your network has some issues, or your proxy doesn't work. Try another proxy or find out the network issue.

Q: MIC complains "Error <repo>: found 1 resolver problem, abort!"

A: This is not an issue with MIC, but with the repo you used. Make sure the packages in the repo you used have proper dependencies.

Q: I used '-A i586' to create an i586 image, but it showed "nothing provided ....". What's wrong with it?

A: Use '-A i686'. i586 is lower than i686, so many packages will be missing from the installation.

Q: MIC shows in the log: "file /usr/share/whatever conflicts between attempted installs of somepackageA and somepackageB"

A: There are conflicts between some packages in the repo you used, but this is not an issue with MIC. Please make sure you are using a proper repo.

Q: Error shows: Command 'modprobe' is not available in Fedora 17.

A: In Fedora 17, when you use sudo, the PATH variable will be changed and you will lose some important paths. Run 'export PATH=/sbin:$PATH' before running MIC.


