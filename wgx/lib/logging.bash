#!/usr/bin/env bash

log(){ printf "%s\n" "$*" >&2; }
die(){ echo "ERR: $*" >&2; exit 1; }
