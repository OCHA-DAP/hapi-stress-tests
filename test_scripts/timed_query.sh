#!/bin/bash

QUERY_FILE="$1"
NUM_ITERATIONS=100
DB_CONTAINER="hapi-stress-test-db"

# Function to extract the real time from the 'EXPLAIN ANALYZE' output
get_real_time() {
    echo "$1" | grep "Execution Time: " | awk '{print $3}'
}

total_time=0
for ((i=1; i<=NUM_ITERATIONS; i++))
do
    echo "Iteration $i:"
    iteration_output=$(cat "$QUERY_FILE" | docker exec -i $DB_CONTAINER psql -h localhost -U postgres -d hapi 2>&1)
    echo "$iteration_output"
    iteration_time=$(get_real_time "$iteration_output")
    total_time=$(bc <<< "$total_time + $iteration_time")
    echo ""
done

average_time=$(bc <<< "scale=3; $total_time / $NUM_ITERATIONS / 1000")
echo "Average Time: $average_time s"
