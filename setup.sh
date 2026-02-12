#!/bin/bash
# Setup script for Browser4Programer

echo "=================================="
echo "Browser4Programer Setup"
echo "=================================="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo
    echo "⚠️  Please edit .env and add your API key!"
    echo
else
    echo "✓ .env file already exists"
    echo
fi

# Create workspace directory
echo "Creating workspace directory..."
mkdir -p workspace
mkdir -p output
echo "✓ Directories created"
echo

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI or Anthropic API key"
echo "2. Run the demo: python examples/demo.py"
echo "3. Try an example: python main.py --example"
echo "4. Or run your own task: python main.py \"Your task here\""
echo
