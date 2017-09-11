#!/bin/bash

TMP_SCRIPT=/tmp/forever-babao-tmp.sh
LOG_DIR=~/.babao.d/log  # TODO

GREEN="\033[32;01m"
WHITE="\033[37;01m"
RESET="\033[0m"

rm -f ~/.babao.d/*lock

cat > $TMP_SCRIPT << EOF
#!/bin/bash

function log_exec() {
    echo -e "$WHITE\$(date "+[%Y/%m/%d %H:%M:%S]")$GREEN [FOREVER]$RESET \$@"
    \$@
}

while true; do
    log_exec babao $@
done
EOF
chmod 755 $TMP_SCRIPT

nohup $TMP_SCRIPT >> $LOG_DIR/babao.log 2>&1 &
