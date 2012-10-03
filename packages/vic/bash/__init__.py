"""
# Install 'most'
$ sudo aptitude install most
# Configure 'most' to handle man pages (~/.bashrc)
$ export MANPAGER="/usr/bin/most -s"


if [ "$color_prompt" = yes ]; then
    blackf=$(tput setaf 0)
    green=$(tput setaf 2)
    blue=$(tput setaf 4)
    bold=$(tput bold)
    red=$(tput setaf 1)
    yellow=$(tput setaf 3)
    und=$(tput sgr 0 1)
    reset=$(tput sgr0)
    PS1='${debian_chroot:+($debian_chroot)}\[\[$bold$green\]\u@:\[$blue\]\w\[$yellow\]$(__git_ps1)\[$reset\] \$ '

    
export EDITOR=emacs
export MANPAGER="/usr/bin/most -s"
export GIT_PS1_SHOWDIRTYSTATE=true

"""