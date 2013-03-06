local return_code="%(?..%{$fg[red]%}%?↵ )"

function virtualenv_info {
    [ $VIRTUAL_ENV ] && echo '['`basename $VIRTUAL_ENV`'] '
}

PROMPT='%B${return_code}%{$fg[green]%}$(virtualenv_info)%{$fg[grey]%}%n@%m %{$fg[yellow]%}${PWD/#$HOME/~} $(git_prompt_info)%{$fg[white]%}»%b '
RPS1=""

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[blue]%}("
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$fg[blue]%}) "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[yellow]%} *"
