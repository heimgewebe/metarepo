_just() {
  local i cur prev words opts cmd
  COMPREPLY=()

  # Modules use "::" as the separator, which is considered a wordbreak character in bash.
  # The _get_comp_words_by_ref function is a hack to allow for exceptions to this rule without
  # modifying the global COMP_WORDBREAKS environment variable.
  if type _get_comp_words_by_ref &> /dev/null; then
    _get_comp_words_by_ref -n : cur prev words
  else
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"
    words=("${COMP_WORDS[@]}")

    local idx=$COMP_CWORD
    while [[ $idx -gt 0 ]]; do
      if [[ "${COMP_WORDS[idx - 1]}" == ":" ]]; then
        cur="${COMP_WORDS[idx - 1]}$cur"
        idx=$((idx - 1))
      elif [[ $idx -lt $COMP_CWORD ]]; then
        cur="${COMP_WORDS[idx - 1]}$cur"
        idx=$((idx - 1))
        break
      else
        break
      fi
    done
  fi

  cmd=""
  opts=""

  for i in "${words[@]}"; do
    case "${cmd},${i}" in
      ",$1")
        cmd="just"
        ;;
      *) ;;
    esac
  done

  case "${cmd}" in
    just)
      opts="-E -n -g -f -q -u -v -d -c -e -l -s -h -V --alias-style --ceiling --check --chooser --clear-shell-args --color --command-color --cygpath --dotenv-filename --dotenv-path --dry-run --dump-format --explain --global-justfile --highlight --justfile --list-heading --list-prefix --list-submodules --no-aliases --no-deps --no-dotenv --no-highlight --one --quiet --allow-missing --set --shell --shell-arg --shell-command --tempdir --timestamp --timestamp-format --unsorted --unstable --verbose --working-directory --yes --changelog --choose --command --completions --dump --edit --evaluate --fmt --groups --init --list --man --request --show --summary --variables --help --version [ARGUMENTS]..."
      if [[ ${cur} == -* ]]; then
        mapfile -t COMPREPLY < <(compgen -W "${opts}" -- "${cur}")
        return 0
      else
        local recipes
        recipes=$(just --summary 2> /dev/null)

        if echo "${cur}" | \grep -qF '/'; then
          local path_prefix
          path_prefix=$(echo "${cur}" | sed 's/[/][^/]*$/\//')
          recipes=$(just --summary -- "${path_prefix}" 2> /dev/null)
          # shellcheck disable=SC2086
          recipes=$(printf "${path_prefix}%s\t" $recipes)
        fi

        if just --summary &> /dev/null; then
          mapfile -t COMPREPLY < <(compgen -W "${recipes}" -- "${cur}")
          if type __ltrim_colon_completions &> /dev/null; then
            __ltrim_colon_completions "$cur"
          elif [[ "$cur" == *:* ]]; then
            local col_prefix="${cur%${COMP_WORDS[COMP_CWORD]}}"
            local i
            for i in "${!COMPREPLY[@]}"; do
              local val="${COMPREPLY[$i]}"
              if [[ "$val" == "$col_prefix"* ]]; then
                COMPREPLY[$i]="${val#$col_prefix}"
              fi
            done
          fi
          return 0
        fi
      fi
      case "${prev}" in
        --alias-style)
          mapfile -t COMPREPLY < <(compgen -W "left right separate" -- "${cur}")
          return 0
          ;;
        --ceiling)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --chooser)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --color)
          mapfile -t COMPREPLY < <(compgen -W "always auto never" -- "${cur}")
          return 0
          ;;
        --command-color)
          mapfile -t COMPREPLY < <(compgen -W "black blue cyan green purple red yellow" -- "${cur}")
          return 0
          ;;
        --cygpath)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --dotenv-filename)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --dotenv-path)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -E)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --dump-format)
          mapfile -t COMPREPLY < <(compgen -W "json just" -- "${cur}")
          return 0
          ;;
        --justfile)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -f)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --list-heading)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --list-prefix)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --set)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --shell)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --shell-arg)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --tempdir)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --timestamp-format)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --working-directory)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -d)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --command)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -c)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --completions)
          mapfile -t COMPREPLY < <(compgen -W "bash elvish fish nushell powershell zsh" -- "${cur}")
          return 0
          ;;
        --list)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -l)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --request)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        --show)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        -s)
          mapfile -t COMPREPLY < <(compgen -f "${cur}")
          return 0
          ;;
        *)
          COMPREPLY=()
          ;;
      esac
      mapfile -t COMPREPLY < <(compgen -W "${opts}" -- "${cur}")
      return 0
      ;;
  esac
}

if [[ "${BASH_VERSINFO[0]}" -eq 4 && "${BASH_VERSINFO[1]}" -ge 4 || "${BASH_VERSINFO[0]}" -gt 4 ]]; then
  complete -F _just -o nosort -o bashdefault -o default just
else
  complete -F _just -o bashdefault -o default just
fi
