#!/bin/bash -ex

#TODO:
# calc sar in file2
# dump transaction to ledger

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SLEEP_DELAY=60
# TIME_INTERVAL=5
ASSET_PAIR=XXBTZEUR
LOG_DIR="$HERE/log"
DATA_DIR="$HERE/data"
CONFIG_DIR="$HERE/config"
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

function print_error() {
    echo -e "$CLR_RED""ERROR: $CLR_WHITE$1$CLR_RESET" >&2
}

# function calc_psar() {
#     for i in $1; do
#         echo "--- $i ---"
#         TODO
#     done
# }


function dump_OHLC() {
    # Store recents OpenHighLowClose prices to file

    tmp="$LOG_DIR/babao.tmp"
    req="$LOG_DIR/babao.request"

    # we'll update records for all time interval
    for time in 1 5 15 30 60 240 1440 10080 21600; do
        last_dump="$DATA_DIR/last_dump-$ASSET_PAIR-$time.timestamp"
        dump_file="$DATA_DIR/OHLC-$ASSET_PAIR-$time.csv"

        # we loop in case of request error (503...)
        while true; do
            curl -X POST --max-time 90 "$KRAKEN_URL/public/OHLC" --data "\
pair=$ASSET_PAIR&\
interval=$time&\
since=$(test -e "$last_dump" && cat "$last_dump")" > "$req"
            test "$(jq ".error[0]" < "$req")" == "null" && break || true
            print_error "curl request failed (OHLC)"
            sleep 3
        done

        # ideally this should be done after we are sure everything is dumped
        jq -r ".result.last" < "$req" > "$last_dump"
        unset last_dump

        test -e "$dump_file" || \
            echo "time,open,high,low,close,vwap,volume,count" > "$dump_file"
        jq -r ".result.$ASSET_PAIR[] | @csv" < "$req" | sed 's/"//g' > "$tmp"
        mv "$tmp" "$req" #TODO: not sure this is needed

        # remove last entry from dump if the timestamps match (no duplicate)
        test "$(head -n1 "$req" | cut -d, -f1)" \
             == "$(tail -n1 "$dump_file" | cut -d, -f1)" \
            && head -n-1 "$dump_file" > "$tmp" && mv "$tmp" "$dump_file"

        cat "$req" >> "$dump_file"
        unset dump_file

        # calc_psar "$res"

        sleep 3
    done


    #TODO: this is redudant

    # update raw trade data
    last_dump="$DATA_DIR/last_dump-$ASSET_PAIR.timestamp"
    dump_file="$DATA_DIR/trade-$ASSET_PAIR.csv"

    # we loop in case of request error (503...)
    while true; do
        curl -X POST --max-time 90 "$KRAKEN_URL/public/Trades" --data "\
pair=$ASSET_PAIR&\
since=$(test -e "$last_dump" && cat "$last_dump")" > "$req"
        test "$(jq ".error[0]" < "$req")" == "null" && break || true
        print_error "curl request failed (Trades)"
        sleep 3
    done

    test -e "$dump_file" || echo "time,price,volume" > "$dump_file"
    jq -r ".result.XXBTZEUR[] | [.[2], .[:2][]] | @csv" < "$req" | sed 's/"//g' >> "$dump_file"

    jq -r ".result.last" < "$req" > "$last_dump"

    rm -f "$tmp" "$req"
    unset tmp req last_dump
}


FUN_LIST="dump_OHLC"

mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"

while true; do
    for fun in $FUN_LIST; do
	      log="$LOG_DIR/babao_$fun.log"
        echo -e "

********************************************************************************
                        $(date)
********************************************************************************

" >> "$log"
		    $fun |& tee --append "$log"
		    test "${PIPESTATUS[0]}" -eq 0
    done
    sleep $SLEEP_DELAY
done
