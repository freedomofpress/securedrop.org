Rebuilding CI container
-----------------------

* If you are running grsec, ensure chroot_deny_chmod is off. Easiest way to do
  that temporarily is `sudo sysctl -w kernel.grsecurity.chroot_deny_chmod=0 ` 
* From the root dir run `molecule converge -s buildci` 
* Then commit that image: `docker commit debian_jessie_pftracker_ci_base quay.io/freedomofpress/ci-webserver`
* Finally push that image and record the digest results in `./molecule/docker_hashes.yml`

(Be careful when pushing, you might break other roles that rely on this image if you dont change the tag).
