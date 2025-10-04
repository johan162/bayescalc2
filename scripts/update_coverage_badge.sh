#!/bin/bash
# Update coverage badge in README.md with actual coverage from coverage.xml

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# File paths
COVERAGE_XML="coverage.xml"
README_FILE="README.md"

# Check if coverage.xml exists
if [ ! -f "$COVERAGE_XML" ]; then
    echo -e "${RED}❌ Error: coverage.xml not found${NC}"
    echo "Run pytest with coverage first: pytest --cov=src/bayescalc --cov-report=xml"
    exit 1
fi

# Check if README.md exists
if [ ! -f "$README_FILE" ]; then
    echo -e "${RED}❌ Error: README.md not found${NC}"
    exit 1
fi

# Extract line-rate from coverage.xml
# The coverage XML format: <coverage line-rate="0.8345" ...>
line_rate=$(grep -o '<coverage[^>]*line-rate="[0-9.]*"' "$COVERAGE_XML" | grep -o 'line-rate="[0-9.]*"' | cut -d'"' -f2)

if [ -z "$line_rate" ]; then
    echo -e "${RED}❌ Error: Could not extract line-rate from coverage.xml${NC}"
    exit 1
fi

# Convert to percentage and round to 2 decimal places
coverage_percent=$(echo "$line_rate * 100" | bc -l | xargs printf "%.0f")

echo -e "${BLUE}📊 Coverage line-rate: ${line_rate}${NC}"
echo -e "${BLUE}📊 Coverage percentage: ${coverage_percent}%${NC}"

# Determine badge color based on coverage
if [ "$coverage_percent" -ge 90 ]; then
    badge_color="brightgreen"
elif [ "$coverage_percent" -ge 80 ]; then
    badge_color="darkgreen"
elif [ "$coverage_percent" -ge 70 ]; then
    badge_color="yellowgreen"
elif [ "$coverage_percent" -ge 60 ]; then
    badge_color="yellow"
elif [ "$coverage_percent" -ge 50 ]; then
    badge_color="orange"
else
    badge_color="red"
fi

echo -e "${BLUE}🎨 Badge color: ${badge_color}${NC}"

# Create the new badge URL
new_badge_url="https://img.shields.io/badge/coverage-${coverage_percent}%25-${badge_color}.svg"

# Update README.md
# Find the line with the coverage badge and replace it
if grep -q "img.shields.io/badge/coverage-" "$README_FILE"; then
    # Use sed to replace the coverage badge URL
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed requires empty string after -i
        sed -i '' "s|https://img.shields.io/badge/coverage-[0-9]*%25-[a-z]*.svg|${new_badge_url}|g" "$README_FILE"
    else
        # Linux sed
        sed -i "s|https://img.shields.io/badge/coverage-[0-9]*%25-[a-z]*.svg|${new_badge_url}|g" "$README_FILE"
    fi
    echo -e "${GREEN}✅ Updated coverage badge in README.md to ${coverage_percent}%${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Coverage badge not found in README.md${NC}"
    echo "Expected pattern: https://img.shields.io/badge/coverage-XX%25-COLOR.svg"
    exit 1
fi

# Verify the change
if grep -q "coverage-${coverage_percent}%25" "$README_FILE"; then
    echo -e "${GREEN}✅ Verification successful: Badge updated to ${coverage_percent}%${NC}"
else
    echo -e "${RED}❌ Verification failed: Badge may not have been updated correctly${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Coverage badge update complete!${NC}"
