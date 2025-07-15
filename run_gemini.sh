#!/bin/bash

# Source NVM to get node in the PATH
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Execute the original gemini command with all arguments
/mnt/c/Users/rahil/AppData/Roaming/npm/gemini "$@"
