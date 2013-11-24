# Path to your oh-my-zsh configuration.
ZSH=$HOME/.oh-my-zsh

# Set name of the theme to load.
# Look in ~/.oh-my-zsh/themes/
# Optionally, if you set this to "random", it'll load a random theme each
# time that oh-my-zsh is loaded.
# ZSH_THEME="wic"

# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# Set to this to use case-sensitive completion
# CASE_SENSITIVE="true"

# Comment this out to disable bi-weekly auto-update checks
# DISABLE_AUTO_UPDATE="true"

# Uncomment to change how often before auto-updates occur? (in days)
# export UPDATE_ZSH_DAYS=13

# Uncomment following line if you want to disable colors in ls
# DISABLE_LS_COLORS="true"

# Uncomment following line if you want to disable autosetting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment following line if you want to disable command autocorrection
# DISABLE_CORRECTION="true"

# Uncomment following line if you want red dots to be displayed while waiting for completion
# COMPLETION_WAITING_DOTS="true"

# Uncomment following line if you want to disable marking untracked files under
# VCS as dirty. This makes repository status check for large repositories much,
# much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
#plugins=(git)

source $ZSH/oh-my-zsh.sh

local return_code="%(?..%{$fg[red]%}%? )"

function virtualenv_info {
    [ $VIRTUAL_ENV ] && echo "[$(basename $VIRTUAL_ENV)] "
}
export PROJECT_HOME=~/projects/
export WORKON_HOME=~/projects/venv
#export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUAL_ENV_DISABLE_PROMPT=1

if [ -f "$(which virtualenvwrapper_lazy.sh)" ]; then
    source $(which virtualenvwrapper_lazy.sh)
fi

PROMPT='%B${return_code}%{$fg[green]%}$(virtualenv_info)%{$fg[grey]%}%n@%m %{$fg[yellow]%}${PWD/#$HOME/~} $(git_prompt_info)%{$fg[white]%}$%b '
RPS1=""

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[blue]%}("
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$fg[blue]%}) "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[yellow]%} *"

export EDITOR=emacs
export MANPAGER="/usr/bin/most -s"

disable -r time       # disable shell reserved word

if [ -f ~/projects/devenv.sh ]; then
    source ~/projects/devenv.sh
fi
