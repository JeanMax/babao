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

print_error() {
    date >&2
    echo -e "$CLR_RED""ERROR: $CLR_WHITE$1$CLR_RESET" >&2
}

dump_api_data() {
    tmp="$LOG_DIR/babao.tmp"
    req="$LOG_DIR/babao.request"
    last_dump="$DATA_DIR/last_dump-$ASSET_PAIR.timestamp"
    raw_data_file="$DATA_DIR/trade-$ASSET_PAIR.csv"
    # beware the missing "$DATA_DIR/"
    last_raw_data_dump="last_dump-trade-$ASSET_PAIR.csv"

    # we loop in case of request error (503...)
    while true; do
        curl -sS --max-time 90 -o "$req" \
             -X POST "$KRAKEN_URL/public/Trades" --data "\
pair=$ASSET_PAIR&\
since=$(test -e "$last_dump" && cat "$last_dump")" || true
        test "$(jq ".error[0]" < "$req")" == "null" && break || true
        print_error "curl request failed (Trades)"
        sleep 3
    done

    set +e
    trap 'echo -e "\nTerminating..."; EXIT=42' EXIT INT TERM
    # test -e "$raw_data_file" || echo "time,price,volume" > "$raw_data_file"
    jq -r ".result.XXBTZEUR[] | [(.[2] | floor), (.[:2][] | tonumber)] | @csv" \
       < "$req" > "$DATA_DIR/$last_raw_data_dump"

    /usr/bin/env python $PYTHON_FLAGS \
                 "$SRC_DIR/resample-data.py" \
                 "$DATA_DIR/$last_raw_data_dump" \
                 "$TIME_INTERVAL" \
                 "$DATA_DIR/$(echo "$last_raw_data_dump" | cut -d- -f2- | cut -d. -f-1)" &
    child=$!

    cat "$DATA_DIR/$last_raw_data_dump" >> "$raw_data_file"
    jq -r ".result.last" < "$req" > "$last_dump"

    rm -f "$tmp" "$req"
    unset tmp req last_dump


    wait "$child"
    trap - EXIT INT TERM && test "$EXIT" && kill -INT $$
    set -e
}



if [ "$DEBUG" ]; then
    set -x
    # PYTHON_FLAGS="-m trace -t"
fi

mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"

FUN_LIST="dump_api_data"

while true; do
    # time (
        for fun in $FUN_LIST; do
	          log="$LOG_DIR/babao_$fun.log"
		        $fun >> "$log" 2>&1  #TODO: it would be nice to tee it, but it's annoying with signals
        done
    # )
    sleep $SLEEP_DELAY
done
