#######################################
### update pc in the git ###
#######################################

#copy all costum pc files
cp -r -b /home/blade/.config/i3/* /home/blade/git/blade/i3wm/pc_config
cp -r -b /home/blade/scripts/* /home/blade/git/blade/pc_scripts

#add them to the git
cd /home/blade/git/blade/i3wm/pc_config
git add .
cd /home/blade/git/blade/pc_scripts
git add .

#shows u changes
git status

#commit  changes
git commit -m "update pc files"

#pushes changes into git
git push

