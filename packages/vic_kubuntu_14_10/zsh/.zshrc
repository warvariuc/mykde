ZSH=$HOME/.oh-my-zsh

plugins=(git, python)

. $ZSH/oh-my-zsh.sh

local return_code="%(?..%{$fg[red]%}%? )"

function virtualenv_info {
    [ $VIRTUAL_ENV ] && echo '['`basename $VIRTUAL_ENV`'] '
}

PROMPT='%B${return_code}%{$fg[green]%}$(virtualenv_info)%{$fg[grey]%}%n@%m %{$fg[yellow]%}${PWD/#$HOME/~} $(git_prompt_info)%{$fg[white]%}$%b '
RPS1=""

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[blue]%}("
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$fg[blue]%}) "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[yellow]%} *"

# Customize to your needs...
# export PATH=$PATH:/usr/lib/x86_64-linux-gnu/qt4/bin:/usr/lib/lightdm/lightdm:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games

export PROJECT_HOME=~/projects/
export WORKON_HOME=~/projects/venv
#export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUAL_ENV_DISABLE_PROMPT=1

. virtualenvwrapper_lazy.sh 2>/dev/null

export EDITOR=emacs
export PAGER="/usr/bin/most -s"

disable -r time       # disable shell reserved word

[ -f "$HOME/projects/devenv.sh" ] && . "$HOME/projects/devenv.sh"
