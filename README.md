# 📊 AI CFO - Local Offline Finance AI

A local offline financial analysis assistant powered by Phi-3 Mini (3B parameter model) via Ollama. The model performs reasoning but **NEVER** performs calculations - all calculations are handled by a Python-based finance SDK.

## Features

- **Local & Offline**: No external APIs, fully private
- **Tool-Based Architecture**: LLM never calculates - uses deterministic Python functions
- **Multiple Interfaces**: CLI and Streamlit UI
- **Financial Tools**: NPV, IRR, ROI, Break-Even, Financial Ratios

## Quick Start

### 1. Setup

```bash
cd "/home/vansh/vansh private/AI CFO"

# Run setup script (creates venv, installs dependencies and Ollama)
chmod +x setup.sh
./setup.sh
```

### 2. Start Ollama

```bash
ollama serve
```

### 3. Run AI CFO

**CLI Mode:**
```bash
# Using virtual environment
./venv/bin/python cli.py

# Or directly if dependencies installed globally
python3 cli.py
```

**Streamlit UI:**
```bash
./venv/bin/streamlit run app.py
```

**Single Query:**
```bash
./venv/bin/python cli.py -q "Calculate NPV with cashflows [-1000, 300, 400, 500] at 10% rate"
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `npv` | Net Present Value | `cashflows`, `rate` |
| `irr` | Internal Rate of Return | `cashflows` |
| `roi` | Return on Investment | `gain`, `cost` |
| `break_even` | Break-Even Point | `fixed_cost`, `price`, `variable_cost` |
| `financial_ratios` | Financial Ratio Analysis | `balance_sheet`, `income_statement` |

## Example Queries

```
• "Calculate NPV with cashflows [-1000, 300, 400, 500] at 10% discount rate"
• "What's the IRR for investment with cashflows [-5000, 1500, 2000, 2500]?"
• "Calculate ROI if gain is 15000 and cost is 10000"
• "I need break-even analysis with fixed cost 10000, price 50, variable cost 30"
• "Analyze financial ratios for my company"
```

## Architecture

```
User Input → Phi-3 Mini → JSON Tool Call → Python SDK → Result → Phi-3 Mini → Final Answer
```

### Components

- **`finance_tools.py`**: Core SDK with deterministic financial functions
- **`orchestrator.py`**: Model interaction, tool calling, response generation
- **`cli.py`**: Command-line interface
- **`app.py`**: Streamlit web interface
- **`test_finance_tools.py`**: Test cases for all functions

## System Requirements

- Python 3.8+
- Ollama
- Phi-3 Mini model (auto-pulled by setup script)

## Dependencies

```
numpy>=1.24.0
pandas>=2.0.0
streamlit>=1.28.0
requests>=2.31.0
pytest>=7.4.0
```

## Testing

```bash
# Run all tests
pytest test_finance_tools.py -v

# Run specific test class
pytest test_finance_tools.py::TestNPV -v
```

## Project Structure

```
AI CFO/
├── finance_tools.py      # Core finance SDK
├── orchestrator.py       # Model orchestration & tool calling
├── cli.py                # CLI interface
├── app.py                # Streamlit UI
├── test_finance_tools.py # Test cases
├── setup.sh              # Setup script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Constraints

- ✅ Fully offline system
- ✅ No external APIs
- ✅ Optimized for speed and low memory
- ✅ Modular and extensible code

## License

MIT
