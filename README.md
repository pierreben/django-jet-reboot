I couldn't recompile the build js file using gulp task because I had no time and :

- The sass version needs node v7
- It's possible to launch the task via: ./node_modules/gulp/bin/gulp.js scripts but it fails because some dependencies sources coming from github (like perfect-scrollbar/jquery) seems not to exist any longer at the good version (compared to the version I used in the past with django-jet)
- I already had a compile version of bundle.min.js and it looks that no changed was made to this file since 2017 (https://github.com/assem-ch/django-jet-reboot/tree/master/jet/static/jet/js/build), so as I had really no time, I kept my already compiled version



