#!/bin/bash
# Bash script to install Git hooks and pre-commit
# Run this after cloning the repository

echo "🔧 Setting up Git hooks and pre-commit..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install pre-commit"
        exit 1
    fi
fi

# Install pre-commit hooks
echo "🎣 Installing pre-commit hooks..."
pre-commit install --install-hooks
pre-commit install --hook-type pre-push

if [ $? -ne 0 ]; then
    echo "❌ Failed to install pre-commit hooks"
    exit 1
fi

# Copy custom Git hooks
hooks_dir=".git/hooks"
if [ -d "$hooks_dir" ]; then
    echo "📋 Installing custom Git hooks..."

    if [ -f ".github/hooks/pre-commit" ]; then
        cp .github/hooks/pre-commit "$hooks_dir/pre-commit"
        chmod +x "$hooks_dir/pre-commit"
        echo "  ✅ pre-commit hook installed"
    fi

    if [ -f ".github/hooks/pre-push" ]; then
        cp .github/hooks/pre-push "$hooks_dir/pre-push"
        chmod +x "$hooks_dir/pre-push"
        echo "  ✅ pre-push hook installed"
    fi
fi

# Test pre-commit installation
echo ""
echo "🧪 Testing pre-commit installation..."
pre-commit run --all-files

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Git hooks setup complete!"
    echo ""
    echo "ℹ️  Hooks installed:"
    echo "  • pre-commit: Runs linters and formatters before each commit"
    echo "  • pre-push: Runs full test suite before pushing"
    echo ""
    echo "💡 To skip hooks temporarily, use: git commit --no-verify"
else
    echo ""
    echo "⚠️  Some pre-commit checks failed. Fix the issues and run:"
    echo "  pre-commit run --all-files"
fi
