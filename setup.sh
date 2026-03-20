#!/bin/bash
# AI CFO Setup Script
# Installs dependencies and configures Ollama with Phi-3 Mini

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              📊 AI CFO - Setup Script                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
echo -e "${YELLOW}[1/5] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if pip is available
echo -e "${YELLOW}[2/5] Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip3 available${NC}"
else
    echo -e "${RED}✗ pip3 not found. Please install pip.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}[3/5] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}[4/5] Installing Python dependencies...${NC}"
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if Ollama is installed
echo -e "${YELLOW}[5/5] Checking Ollama installation...${NC}"
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version)
    echo -e "${GREEN}✓ Found: $OLLAMA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Ollama not found. Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
fi

# Pull Phi-3 Mini model
echo -e "${YELLOW}[6/6] Pulling Phi-3 Mini model...${NC}"
ollama pull phi3:mini
echo -e "${GREEN}✓ Phi-3 Mini model ready${NC}"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Start Ollama:  ollama serve"
echo "  2. Run CLI:       python3 cli.py"
echo "  3. Run UI:        streamlit run app.py"
echo ""
echo -e "${YELLOW}Quick test:${NC}"
echo "  python3 cli.py -q \"Calculate NPV with cashflows [-1000, 300, 400, 500] at 10% rate\""
echo ""
