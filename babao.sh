#!/bin/bash -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SLEEP_DELAY=60
TIME_INTERVAL=5
ASSET_PAIR=XXBTZEUR
LOG_DIR="$HERE/log"
DATA_DIR="$HERE/data"
CONFIG_DIR="$HERE/config"
SRC_DIR="$HERE/src"
KRAKEN_URL="https://api.kraken.com/0"

# beware the missing "$DATA_DIR/"
LAST_RAW_DATA_DUMP="last_dump-trade-$ASSET_PAIR.csv"

# shellcheck disable=SC1090
source "$CONFIG_DIR/babao.conf"

# CLR_BLACK="\033[30;01m"
CLR_RED="\033[31;01m"
# CLR_GREEN="\033[32;01m"
# CLR_YELLOW="\033[33;01m"
# CLR_BLUE="\033[34;01m"
# CLR_MAGENTA="\033[35;01m"
# CLR_CYAN="\033[36;01m"
CLR_WHITE="\033[37;01m"
CLR_RESET="\033[0m"

function print_error() {
    date >&2
    echo -e "$CLR_RED""ERROR: $CLR_WHITE$1$CLR_RESET" >&2
}

function update_indicators() {
    # every indicator SCRIPT takes a raw trade data FILE as parameter
    # it adds the results to SCRIPT-FILE with the coresponding timestamps

    #meh
    echo -n ''
}

function resample_data() {
    /usr/bin/env python $PYTHON_FLAGS \
                 "$SRC_DIR/resample-data.py" \
                 "$DATA_DIR/$LAST_RAW_DATA_DUMP" \
                 "$TIME_INTERVAL" \
                 "$DATA_DIR/$(echo "$LAST_RAW_DATA_DUMP" | cut -d- -f2- | cut -d. -f-1)" \
                 # | grep resample-data.py # DEBUG
}

function dump_api_data() {
    tmp="$LOG_DIR/babao.tmp"
    req="$LOG_DIR/babao.request"
    last_dump="$DATA_DIR/last_dump-$ASSET_PAIR.timestamp"
    raw_data_file="$DATA_DIR/trade-$ASSET_PAIR.csv"

    # we loop in case of request error (503...)
    while true; do
        curl -sS --max-time 90 -o "$req" \
             -X POST "$KRAKEN_URL/public/Trades" --data "\
pair=$ASSET_PAIR&\
since=$(test -e "$last_dump" && cat "$last_dump")"
        test "$(jq ".error[0]" < "$req")" == "null" && break || true
        print_error "curl request failed (Trades)"
        sleep 3
    done

    # test -e "$raw_data_file" || echo "time,price,volume" > "$raw_data_file"
    jq -r ".result.XXBTZEUR[] | [(.[2] | floor), (.[:2][] | tonumber)] | @csv" \
       < "$req" > "$DATA_DIR/$LAST_RAW_DATA_DUMP"
    cat "$DATA_DIR/$LAST_RAW_DATA_DUMP" >> "$raw_data_file"

    jq -r ".result.last" < "$req" > "$last_dump"

    rm -f "$tmp" "$req"
    unset tmp req last_dump
}



if [ "$DEBUG" ]; then
    set -x
    PYTHON_FLAGS="-m trace -t"
fi

mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"

FUN_LIST="dump_api_data
resample_data
update_indicators"

status_file="$LOG_DIR/babao.status" #TODO: remove that and trap signals
while true; do
    # time (
        for fun in $FUN_LIST; do
	          log="$LOG_DIR/babao_$fun.log"
            echo "working on $fun" > "$status_file"
		        $fun |& tee --append "$log"
		        test "${PIPESTATUS[0]}" -eq 0
        done
    # )
    echo "just chillin" > "$status_file"
    sleep $SLEEP_DELAY
done
