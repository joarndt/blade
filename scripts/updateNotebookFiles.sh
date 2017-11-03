#######################################
### update notebookfiles in the git ###
#######################################

#copy all costum notebookfiles
cp -r -b /home/blade/.config/i3/* /home/blade/git/blade/i3wm/notebook_config
cp -r -b /home/blade/scripts/* /home/blade/git/blade/scripts

#add them to the git
cd /home/blade/git/blade/i3wm/notebook_config
git add .
cd /home/blade/git/blade/scripts
git add .

#commit  changes
git commit -m "update notebook files"

#push them into git
git push
