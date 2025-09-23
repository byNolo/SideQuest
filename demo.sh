#!/bin/bash

# SideQuest Demo - Show quest variety
echo "🎮 SideQuest Demo - Quest Generation Variety"
echo "============================================="
echo ""

users=("alice" "bob" "charlie" "diana" "eve" "frank" "grace" "henry")

echo "Generating quests for different users:"
echo ""

for user in "${users[@]}"; do
    echo -n "👤 $user: "
    quest_info=$(curl -s -H "X-Debug-User: $user" http://localhost:8080/api/quests/today | jq -r '{title: .title, rarity: .rarity} | "\(.title) (\(.rarity))"')
    echo "$quest_info"
    sleep 0.5
done

echo ""
echo "🌤️  Current weather integration:"
weather=$(curl -s -H "X-Debug-User: demo" http://localhost:8080/api/quests/today | jq -r '.weather.description // "Weather data unavailable"')
echo "   $weather"

echo ""
echo "📊 Available quest templates:"
template_count=$(curl -s http://localhost:8080/api/templates | jq '.templates | length')
echo "   $template_count templates loaded"

echo ""
echo "✅ All systems operational!"
echo ""
echo "🌐 Visit: http://localhost:8080"
echo "📋 Status: make status"
echo "📖 Progress: cat PROGRESS.md"