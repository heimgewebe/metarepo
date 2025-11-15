#!/usr/bin/env bash

cmd_smoke(){
  local count; count="$(ordered_repos | sed '/^$/d' | wc -l | tr -d ' ')"
  echo "Repos in scope: ${count:-0}"
}
