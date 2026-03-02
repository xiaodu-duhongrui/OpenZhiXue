#!/bin/bash

# OpenZhixue Platform - Database Reset Script
# This script resets all databases to their initial state

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "  Database Reset Script"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will delete all data in the databases!"
echo ""
read -p "Are you sure you want to continue? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Operation cancelled."
    exit 0
fi

cd "$PROJECT_ROOT"

echo ""
echo "🛑 Stopping PostgreSQL container..."
docker-compose stop postgres

echo "🗑️  Removing PostgreSQL data volume..."
docker-compose rm -f -v postgres

echo "🔄 Starting PostgreSQL with fresh data..."
docker-compose up -d postgres

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U openzhixue 2>/dev/null; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    echo "   Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ PostgreSQL failed to start within timeout"
    exit 1
fi

echo ""
echo "✅ Database has been reset successfully!"
echo ""
echo "📊 The following databases have been recreated:"
echo "   - openzhixue (main)"
echo "   - openzhixue_users"
echo "   - openzhixue_exams"
echo "   - openzhixue_analytics"
echo ""
