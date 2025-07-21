#!/bin/bash

# MOE Trading System Setup Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up MOE Trading System...${NC}"

# Check if conda is installed
if command -v conda >/dev/null 2>&1; then
    echo -e "${GREEN}Conda found. Creating environment...${NC}"
    conda env create -f environment.yml
    
    # Check if environment was created successfully
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Conda environment 'moe_trading' created successfully!${NC}"
        echo -e "${YELLOW}Activate the environment with: ${GREEN}conda activate moe_trading${NC}"
    else
        echo -e "${RED}Failed to create conda environment. Try manual installation:${NC}"
        echo -e "${YELLOW}conda env create -f environment.yml${NC}"
    fi
else
    echo -e "${YELLOW}Conda not found. Attempting pip installation...${NC}"
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Pip packages installed successfully!${NC}"
    else
        echo -e "${RED}Failed to install pip packages. Please check your Python installation and try again.${NC}"
    fi
fi

# Check if config.json exists, if not copy from template
if [ ! -f "config.json" ] && [ -f "config.json.example" ]; then
    echo -e "${YELLOW}Copying config.json.example to config.json...${NC}"
    cp config.json.example config.json
    echo -e "${GREEN}config.json created from example!${NC}"
    echo -e "${YELLOW}Please edit config.json and add your API keys.${NC}"
elif [ ! -f "config.json" ]; then
    echo -e "${YELLOW}Creating config.json template...${NC}"
    cat > config.json << EOF
{
    "openai_api_key": "your_openai_api_key_here",
    "gemini_api_key": "your_gemini_api_key_here"
}
EOF
    echo -e "${GREEN}config.json template created!${NC}"
    echo -e "${YELLOW}Please edit config.json and add your API keys.${NC}"
else
    echo -e "${GREEN}config.json already exists. Skipping creation.${NC}"
fi

echo -e "${GREEN}Setup completed!${NC}"
echo -e "${YELLOW}Run the system with: ${GREEN}python main.py${NC}"