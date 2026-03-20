"""
Test Cases for AI CFO Finance Tools
Tests all financial calculation functions.
"""

import pytest
from finance_tools import (
    npv, irr, roi, break_even, financial_ratios,
    execute_tool, get_available_tools
)


class TestNPV:
    """Test Net Present Value calculations."""
    
    def test_npv_positive(self):
        """Test NPV with positive result."""
        cashflows = [-1000, 300, 400, 500]
        rate = 0.10
        result = npv(cashflows, rate)
        
        assert result["status"] == "success"
        assert "npv" in result
        assert result["npv"] == pytest.approx(-1000 + 300/1.1 + 400/1.1**2 + 500/1.1**3, rel=0.01)
    
    def test_npv_negative(self):
        """Test NPV with negative result."""
        cashflows = [-5000, 500, 600, 700]
        rate = 0.15
        result = npv(cashflows, rate)
        
        assert result["status"] == "success"
        assert result["npv"] < 0
    
    def test_npv_empty_cashflows(self):
        """Test NPV with empty cashflows."""
        result = npv([], 0.10)
        assert result["status"] == "error"
    
    def test_npv_zero_rate(self):
        """Test NPV with zero discount rate."""
        cashflows = [-1000, 500, 500, 500]
        result = npv(cashflows, 0)
        
        assert result["status"] == "success"
        assert result["npv"] == sum(cashflows)


class TestIRR:
    """Test Internal Rate of Return calculations."""
    
    def test_irr_standard(self):
        """Test IRR with standard cashflows."""
        cashflows = [-1000, 300, 400, 500]
        result = irr(cashflows)
        
        assert result["status"] == "success"
        assert "irr" in result
        assert "irr_percentage" in result
        assert result["irr_percentage"] > 0
    
    def test_irr_single_cashflow(self):
        """Test IRR with insufficient cashflows."""
        result = irr([100])
        assert result["status"] == "error"
    
    def test_irr_empty(self):
        """Test IRR with empty cashflows."""
        result = irr([])
        assert result["status"] == "error"


class TestROI:
    """Test Return on Investment calculations."""
    
    def test_roi_profitable(self):
        """Test ROI for profitable investment."""
        result = roi(gain=15000, cost=10000)
        
        assert result["status"] == "success"
        assert result["roi"] == 0.5
        assert result["roi_percentage"] == 50.0
        assert result["net_profit"] == 5000
    
    def test_roi_loss(self):
        """Test ROI for losing investment."""
        result = roi(gain=8000, cost=10000)
        
        assert result["status"] == "success"
        assert result["roi"] < 0
        assert result["net_profit"] < 0
    
    def test_roi_zero_cost(self):
        """Test ROI with zero cost (division by zero)."""
        result = roi(gain=1000, cost=0)
        assert result["status"] == "error"
    
    def test_roi_break_even(self):
        """Test ROI at break-even point."""
        result = roi(gain=10000, cost=10000)
        
        assert result["status"] == "success"
        assert result["roi"] == 0
        assert result["roi_percentage"] == 0


class TestBreakEven:
    """Test Break-Even Point calculations."""
    
    def test_break_even_standard(self):
        """Test standard break-even calculation."""
        result = break_even(fixed_cost=10000, price=50, variable_cost=30)
        
        assert result["status"] == "success"
        assert result["break_even_units"] == 500  # 10000 / (50-30)
        assert result["break_even_revenue"] == 25000
        assert result["contribution_margin"] == 20
    
    def test_break_even_price_equals_variable(self):
        """Test when price equals variable cost."""
        result = break_even(fixed_cost=10000, price=30, variable_cost=30)
        assert result["status"] == "error"
    
    def test_break_even_price_less_than_variable(self):
        """Test when price is less than variable cost."""
        result = break_even(fixed_cost=10000, price=25, variable_cost=30)
        assert result["status"] == "error"
    
    def test_break_even_zero_fixed_cost(self):
        """Test with zero fixed cost."""
        result = break_even(fixed_cost=0, price=50, variable_cost=30)
        
        assert result["status"] == "success"
        assert result["break_even_units"] == 0


class TestFinancialRatios:
    """Test Financial Ratios calculations."""
    
    def test_ratios_complete(self):
        """Test with complete balance sheet and income statement."""
        balance_sheet = {
            "current_assets": 100000,
            "current_liabilities": 50000,
            "total_assets": 500000,
            "total_liabilities": 200000,
            "shareholders_equity": 300000,
            "cash": 30000,
            "accounts_receivable": 20000,
            "inventory": 50000
        }
        
        income_statement = {
            "revenue": 400000,
            "net_income": 60000,
            "cost_of_goods_sold": 200000
        }
        
        result = financial_ratios(balance_sheet, income_statement)
        
        assert result["status"] == "success"
        assert "ratios" in result
        
        ratios = result["ratios"]
        assert ratios["current_ratio"] == 2.0  # 100000/50000
        assert ratios["debt_to_assets"] == 0.4  # 200000/500000
        assert ratios["profit_margin"] == 0.15  # 60000/400000
        assert ratios["return_on_equity"] == 0.2  # 60000/300000
    
    def test_ratios_minimal(self):
        """Test with minimal data."""
        balance_sheet = {
            "current_assets": 50000,
            "current_liabilities": 25000,
            "total_assets": 200000,
            "total_liabilities": 80000,
            "shareholders_equity": 120000
        }
        
        income_statement = {
            "revenue": 150000,
            "net_income": 20000
        }
        
        result = financial_ratios(balance_sheet, income_statement)
        
        assert result["status"] == "success"
        assert result["ratios"]["current_ratio"] == 2.0
        assert result["ratios"]["profit_margin"] > 0
    
    def test_ratios_empty(self):
        """Test with empty data."""
        result = financial_ratios({}, {})
        assert result["status"] == "success"


class TestExecuteTool:
    """Test the tool execution interface."""
    
    def test_execute_npv(self):
        """Test executing NPV tool."""
        result = execute_tool("npv", {"cashflows": [-1000, 500, 500], "rate": 0.1})
        assert result["status"] == "success"
    
    def test_execute_unknown_tool(self):
        """Test executing unknown tool."""
        result = execute_tool("unknown_tool", {})
        assert result["status"] == "error"
        assert "available_tools" in result
    
    def test_execute_invalid_params(self):
        """Test executing with invalid parameters."""
        result = execute_tool("npv", {"wrong_param": 123})
        assert result["status"] == "error"


class TestGetAvailableTools:
    """Test getting available tools."""
    
    def test_tools_available(self):
        """Test that all expected tools are available."""
        tools = get_available_tools()
        
        expected_tools = ["npv", "irr", "roi", "break_even", "financial_ratios"]
        for tool in expected_tools:
            assert tool in tools
            assert "description" in tools[tool]
            assert "parameters" in tools[tool]


# Integration test cases
class TestIntegration:
    """Integration tests for common financial scenarios."""
    
    def test_investment_analysis(self):
        """Test complete investment analysis scenario."""
        # NPV calculation
        npv_result = npv([-50000, 15000, 20000, 25000], 0.10)
        assert npv_result["status"] == "success"
        
        # IRR calculation
        irr_result = irr([-50000, 15000, 20000, 25000])
        assert irr_result["status"] == "success"
        
        # ROI calculation
        total_gain = 15000 + 20000 + 25000
        roi_result = roi(total_gain, 50000)
        assert roi_result["status"] == "success"
        assert roi_result["roi_percentage"] == 20  # (60000-50000)/50000
    
    def test_business_planning(self):
        """Test business planning scenario."""
        # Break-even analysis
        be_result = break_even(fixed_cost=50000, price=100, variable_cost=60)
        assert be_result["status"] == "success"
        assert be_result["break_even_units"] == 1250  # 50000/(100-60)
        
        # Financial ratios for projected statements
        balance_sheet = {
            "current_assets": 200000,
            "current_liabilities": 100000,
            "total_assets": 800000,
            "total_liabilities": 300000,
            "shareholders_equity": 500000,
            "cash": 50000,
            "accounts_receivable": 40000,
            "inventory": 110000
        }
        
        income_statement = {
            "revenue": 600000,
            "net_income": 100000,
            "cost_of_goods_sold": 360000
        }
        
        ratios_result = financial_ratios(balance_sheet, income_statement)
        assert ratios_result["status"] == "success"
        assert ratios_result["ratios"]["current_ratio"] == 2.0
        assert ratios_result["ratios"]["profit_margin"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
