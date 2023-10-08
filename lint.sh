#!/usr/bin/env bash

## PRINTS ##############################################################################

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
readonly RED
readonly GREEN
readonly YELLOW
readonly NC

function print_stderr()
(
    MSG="$1"
    COLOR="${2:-$YELLOW}"
    echo -e "\n${COLOR}${MSG}${NC}" >&2
)

function run_linter_black(){
    print_stderr BLACK
    if [ "$1" = "--check" ]; then
        pipenv run black --check --diff src
    else
        pipenv run black src
    fi
}

run_linter_black $1
