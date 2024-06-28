#!/bin/bash

# Array of state identifiers
states=("al" "ak" "az" "ar" "ca" "co" "ct" "de" "fl" "ga" 
        "hi" "id" "il" "in" "ia" "ks" "ky" "la" "me" "md" 
        "ma" "mi" "mn" "ms" "mo" "mt" "ne" "nv" "nh" "nj" 
        "nm" "ny" "nc" "nd" "oh" "ok" "or" "pa" "ri" "sc" 
        "sd" "tn" "tx" "ut" "vt" "va" "wa" "wv" "wi" "wy")

# Function to run command with timeout and kill process
run_with_timeout() {
    timeout=$1
    shift
    command="$@"
    
    # Run the command in background
    $command &
    pid=$!
    
    # Wait for specified timeout
    for ((i=0; i<$timeout; i++)); do
        if ! kill -0 $pid 2>/dev/null; then
            wait $pid
            return
        fi
        sleep 1
    done
    
    # If we're here, the process is still running
    echo "Timeout reached. Terminating process."
    kill -TERM $pid
    sleep 1
    
    # If it's still not dead, force kill
    if kill -0 $pid 2>/dev/null; then
        echo "Process still running. Force killing."
        kill -9 $pid
    fi
    
    wait $pid
}

# Loop through each state
for state in "${states[@]}"
do
    echo "Processing state: $state"
    echo "-------------------------"
    
    # Run the Docker command with a 20-second timeout
    # Added -T flag to disable pseudo-tty allocation
    run_with_timeout 5 docker-compose run -T --rm scrape $state bills --fastmode --scrape
    
    echo "Finished processing $state"
    echo "-------------------------"
done

echo "All states processed"