local return_code="%(?..%{$fg_bold[red]%}%? ↵%{$reset_color%})"

function virtualenv_info {
    [ $VIRTUAL_ENV ] && echo '['`basename $VIRTUAL_ENV`'] '
}

PROMPT='%B%{$fg[green]%}$(virtualenv_info)%{$fg[grey]%}%n@%m %{$fg[yellow]%}${PWD/#$HOME/~} $(git_prompt_info)%{$fg[white]%}»%b '
RPS1="${return_code}"

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[blue]%}("
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$fg[blue]%}) "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[yellow]%} *"
