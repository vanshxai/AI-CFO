# AI CFO - Comprehensive Test Plan

## Overview
This document outlines the testing strategy for the AI CFO system - a local offline finance AI powered by Phi-3 Mini via Ollama.

---

## Test Categories

### 1. Unit Tests (Finance SDK)
**File:** `test_finance_tools.py`
**Status:** ✅ Already implemented (24 tests)

| Module | Function | Test Cases |
|--------|----------|------------|
| NPV | `npv()` | Positive NPV, Negative NPV, Empty cashflows, Zero rate |
| IRR | `irr()` | Standard IRR, Single cashflow error, Empty error |
| ROI | `roi()` | Profitable, Loss, Zero cost error, Break-even |
| Break-Even | `break_even()` | Standard, Price=variable cost, Price<variable cost, Zero fixed cost |
| Financial Ratios | `financial_ratios()` | Complete data, Minimal data, Empty data |
| Tool Execution | `execute_tool()` | Valid tool, Unknown tool, Invalid params |
| Integration | Multiple | Investment analysis, Business planning |

---

### 2. Integration Tests (Orchestrator)
**File:** `test_orchestrator.py` (To be created)

#### 2.1 Tool Calling System
- [ ] Test JSON extraction from model responses
- [ ] Test valid tool call parsing: `{"tool": "npv", "inputs": {...}}`
- [ ] Test malformed JSON handling
- [ ] Test missing "tool" key handling
- [ ] Test missing "inputs" key handling

#### 2.2 Ollama Communication
- [ ] Test connection to Ollama API
- [ ] Test model availability check
- [ ] Test timeout handling
- [ ] Test connection error handling
- [ ] Test response parsing

#### 2.3 End-to-End Flow
- [ ] User input → Model → Tool → Model → Answer (full cycle)
- [ ] User input → Model → No tool needed → Answer
- [ ] User input → Model → Missing params → Ask user → Tool → Answer

---

### 3. Model Behavior Tests
**File:** `test_model_prompts.py` (To be created)

#### 3.1 System Prompt Adherence
- [ ] Model NEVER performs manual calculations
- [ ] Model ALWAYS calls tools for numerical tasks
- [ ] Model asks for missing inputs before calling tools
- [ ] Model outputs valid JSON for tool calls
- [ ] Model acts as financial analyst (tone check)

#### 3.2 Tool Selection Accuracy
| Query Type | Expected Tool | Test Input |
|------------|---------------|------------|
| NPV query | `npv` | "Calculate NPV with..." |
| IRR query | `irr` | "What's the IRR..." |
| ROI query | `roi` | "Calculate ROI..." |
| Break-even query | `break_even` | "I need break-even..." |
| Ratio analysis | `financial_ratios` | "Analyze my financial ratios..." |

#### 3.3 Edge Cases
- [ ] Ambiguous query handling
- [ ] Multi-step calculation requests
- [ ] Queries outside finance domain
- [ ] Incomplete parameter queries

---

### 4. CLI Tests
**File:** `test_cli.py` (To be created)

#### 4.1 Command Line Arguments
- [ ] `--status` flag shows Ollama status
- [ ] `--tools` flag lists available tools
- [ ] `-q "query"` processes single query
- [ ] `-v` flag shows verbose output
- [ ] `--ollama-url` custom URL support
- [ ] Interactive mode launch (no args)

#### 4.2 Interactive Mode
- [ ] User input prompt works
- [ ] `quit`/`exit`/`q` commands exit gracefully
- [ ] `tools` command shows tools
- [ ] `status` command shows system status
- [ ] KeyboardInterrupt handling (Ctrl+C)

#### 4.3 Output Formatting
- [ ] Colored output in terminal
- [ ] Banner displays correctly
- [ ] Error messages are clear
- [ ] Tool results formatted properly

---

### 5. Streamlit UI Tests
**File:** `test_app.py` (To be created)

#### 5.1 UI Components
- [ ] Page title and icon render
- [ ] Sidebar shows settings
- [ ] Ollama status indicator works
- [ ] Available tools expander shows
- [ ] Clear conversation button works
- [ ] Chat input field functional

#### 5.2 Chat Functionality
- [ ] User messages display correctly
- [ ] Assistant responses display
- [ ] Details expander shows tool info
- [ ] Conversation history persists
- [ ] Spinner shows during processing

#### 5.3 Error States
- [ ] Ollama not running warning shows
- [ ] Model not available warning shows
- [ ] Graceful degradation on errors

---

### 6. Performance Tests
**File:** `test_performance.py` (To be created)

#### 6.1 Response Time
- [ ] Tool execution < 100ms (all functions)
- [ ] Model response < 30s (typical query)
- [ ] Full orchestration cycle < 45s
- [ ] CLI startup time < 2s

#### 6.2 Memory Usage
- [ ] Python process < 500MB baseline
- [ ] No memory leaks in repeated calls
- [ ] Streamlit app < 1GB RAM

#### 6.3 Concurrency (if applicable)
- [ ] Multiple sequential requests handled
- [ ] State isolation between requests

---

### 7. System Tests
**File:** `test_system.py` (To be created)

#### 7.1 Setup Script
- [ ] `setup.sh` runs without errors
- [ ] Virtual environment created
- [ ] Dependencies installed correctly
- [ ] Ollama installation triggered if needed
- [ ] Phi-3 Mini model pulled

#### 7.2 Environment Compatibility
- [ ] Python 3.8+ compatibility
- [ ] Python 3.12 compatibility (current)
- [ ] Linux environment
- [ ] Works without internet (offline mode)

#### 7.3 Ollama Integration
- [ ] Ollama running detection
- [ ] Model availability check
- [ ] API endpoint communication
- [ ] Graceful failure when Ollama stopped

---

### 8. Security Tests
**File:** `test_security.py` (To be created)

#### 8.1 Input Validation
- [ ] SQL injection attempts rejected
- [ ] Code injection in JSON rejected
- [ ] Malformed JSON handled safely
- [ ] Extremely long inputs handled

#### 8.2 Data Privacy
- [ ] No data sent to external APIs
- [ ] Local-only operation verified
- [ ] No logging of sensitive financial data

---

### 9. Regression Tests
**File:** `test_regression.py` (To be created)

#### 9.1 Known Issues
- [ ] NPV calculation accuracy (post-NumPy 1.20)
- [ ] IRR convergence edge cases
- [ ] Division by zero in ratios
- [ ] Empty input handling

---

## Test Execution Plan

### Phase 1: Unit Tests (Existing)
```bash
cd "/home/vansh/vansh private/AI CFO"
./venv/bin/pytest test_finance_tools.py -v
```
**Expected:** 24/24 pass ✅

### Phase 2: Integration Tests
```bash
./venv/bin/pytest test_orchestrator.py -v
./venv/bin/pytest test_model_prompts.py -v
```

### Phase 3: Interface Tests
```bash
./venv/bin/pytest test_cli.py -v
./venv/bin/pytest test_app.py -v
```

### Phase 4: System Tests
```bash
./venv/bin/pytest test_performance.py -v
./venv/bin/pytest test_system.py -v
./venv/bin/pytest test_security.py -v
```

### Phase 5: Full Test Suite
```bash
./venv/bin/pytest tests/ -v --cov=. --cov-report=html
```

---

## Test Data Requirements

### Sample Cashflows
```python
STANDARD_INVESTMENT = [-1000, 300, 400, 500]
HIGH_RETURN = [-5000, 2000, 2500, 3000]
LOW_RETURN = [-10000, 1000, 1500, 2000]
```

### Sample Financial Statements
```python
BALANCE_SHEET = {
    "current_assets": 100000,
    "current_liabilities": 50000,
    "total_assets": 500000,
    "total_liabilities": 200000,
    "shareholders_equity": 300000,
    "cash": 30000,
    "accounts_receivable": 20000,
    "inventory": 50000
}

INCOME_STATEMENT = {
    "revenue": 400000,
    "net_income": 60000,
    "cost_of_goods_sold": 200000
}
```

### Sample Queries
```python
TEST_QUERIES = [
    "Calculate NPV with cashflows [-1000, 300, 400, 500] at 10% rate",
    "What's the IRR for investment [-5000, 1500, 2000, 2500]?",
    "Calculate ROI if gain is 15000 and cost is 10000",
    "Break-even with fixed cost 10000, price 50, variable cost 30",
    "Analyze financial ratios for my company"
]
```

---

## Success Criteria

| Category | Pass Threshold |
|----------|----------------|
| Unit Tests | 100% (24/24) |
| Integration Tests | 95%+ |
| CLI Tests | 100% |
| UI Tests | 90%+ |
| Performance Tests | All under thresholds |
| Security Tests | 100% |

---

## Files to Create

```
tests/
├── test_orchestrator.py      # Orchestrator & tool calling
├── test_model_prompts.py     # Model behavior & prompts
├── test_cli.py               # CLI interface
├── test_app.py               # Streamlit UI
├── test_performance.py       # Performance benchmarks
├── test_system.py            # System integration
├── test_security.py          # Security validation
├── test_regression.py        # Regression tests
└── conftest.py               # Pytest fixtures & config
```

---

## Notes

1. **Ollama Dependency:** Integration tests require Ollama running with phi3:mini model
2. **Offline Testing:** All tests must pass without internet connection
3. **Deterministic Tests:** Unit tests must be deterministic and fast
4. **Mock Support:** Use mocks for Ollama API in unit tests
