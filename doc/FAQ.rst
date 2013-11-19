FAQ
===

Q: When creating an image, MIC shows:
   "Error <creator>: URLGrabber error: http://.../.../repos/oss/ia32/packages/repodata/repomd.xml"

A: Perhaps your network has some issues, or your proxy doesn't work.
   Try another proxy or find out the network issue.

Q: MIC complains "ERROR: found 1 resolver problem, abort!"

A: This is not an issue of MIC, it's caused by the repo you used.
   Make sure the packages in the repo you used have proper dependencies.

Q: I used '-A i586' to create an i586 image, but it showed
   "nothing provided ....". What's wrong with it?

A: Use '-A i686'. i586 is lower than i686, so many packages will be missing
   from the installation.

Q: Error shows: "uninstallable providers: somepackageA"

A: It's caused by the missing package in the repo. To find it out, modify the
   "%packages" section with only one item 'somepackageA' in kickstart file,
   then you can root cause what's the missing dependency.

Q: MIC shows in the log:
   "file /usr/share/whatever conflicts between attempted installs of somepackageA and somepackageB"

A: There are conflicts between some packages in the repo you used, but this
   is not an issue with MIC. Please make sure you are using a proper repo.

Q: Error shows: Command 'modprobe' is not available.

A: In some distributions, when you use sudo, the PATH variable will be changed
   and you will lose some important paths. Run 'export PATH=/sbin:$PATH'
   before running MIC.

Q: MIC lost some packages which are specified in '--includepkgs'/'--excludepkgs'

A: Assume you want to include/exclude some packages in one repo, you will use
   '--includepkgs'/'--excludepkgs' option in the according repo command line,
   but you should list these packages to %packages section too, otherwise they
   will not take any effect.

Q: How does mic select packages? And how to set the priority of a repo?

A: In general, mic will select a higher version if two or more available in
   all repos, if the version is the same, a higher release number is
   prefferred. But if you assign a priority to one repo, mic will prefer to
   select packages from the repo with higher priority, even in case a higher
   version is available in the repo with a lower priority. Actually the
   default priority for a repo is 99, the range of a repo priority is 1~99,
   the larger number has the lower priority.
   An example is given:
     "repo --name=base --baseurl=http://whateverurl --prioirity=1"


