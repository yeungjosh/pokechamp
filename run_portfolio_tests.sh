#!/bin/bash
# Portfolio Test Suite Runner
# Runs comprehensive tests using local_1v1.py (known working script)

echo "======================================================================"
echo "GEN1 AGENT PORTFOLIO TEST SUITE"
echo "======================================================================"
echo "Start time: $(date)"
echo ""

# Create results directory
mkdir -p test_results

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="test_results/portfolio_test_${TIMESTAMP}.txt"

echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Test 1: vs random (20 battles)
echo "📊 Test 1: gen1_agent vs random (20 battles)"
echo "================================================" | tee -a "$RESULTS_FILE"
echo "Test 1: gen1_agent vs random (20 battles)" >> "$RESULTS_FILE"
echo "Timestamp: $(date)" >> "$RESULTS_FILE"
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name random \
    --battle_format gen1ou \
    --N 20 2>&1 | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Test 2: vs max_power (20 battles)
echo "📊 Test 2: gen1_agent vs max_power (20 battles)"
echo "================================================" | tee -a "$RESULTS_FILE"
echo "Test 2: gen1_agent vs max_power (20 battles)" >> "$RESULTS_FILE"
echo "Timestamp: $(date)" >> "$RESULTS_FILE"
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name max_power \
    --battle_format gen1ou \
    --N 20 2>&1 | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Test 3: vs max_damage (20 battles)
echo "📊 Test 3: gen1_agent vs max_damage (20 battles)"
echo "================================================" | tee -a "$RESULTS_FILE"
echo "Test 3: gen1_agent vs max_damage (20 battles)" >> "$RESULTS_FILE"
echo "Timestamp: $(date)" >> "$RESULTS_FILE"
uv run python local_1v1.py \
    --player_name gen1_agent \
    --opponent_name max_damage \
    --battle_format gen1ou \
    --N 20 2>&1 | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Summary
echo "======================================================================"
echo "PORTFOLIO TEST SUITE COMPLETE"
echo "======================================================================"
echo "End time: $(date)"
echo ""
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "To view results:"
echo "  cat $RESULTS_FILE"
