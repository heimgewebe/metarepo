#!/usr/bin/env bash

cmd_guard(){
    echo "Running meta-guard checks..."

    if command -v shellcheck >/dev/null 2>&1; then
      echo "Running shellcheck on wgx/**/*.bash..."
      # bewusst fokussiert auf WGX-Bash-Module; bei Bedarf erweiterbar
      shellcheck -s bash wgx/**/*.bash || exit 1
    else
      echo "shellcheck not found; skipping shell lint."
    fi

    if command -v yamllint >/dev/null 2>&1; then
      echo "Running yamllint..."
      yamllint . || exit 1
    else
      echo "yamllint not found; skipping YAML lint."
    fi

    echo "Guard OK."
}
