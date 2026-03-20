"""
Finance Tools SDK for AI CFO System
Deterministic financial calculation functions.
All calculations are handled here - NEVER by the LLM.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union


def npv(cashflows: List[float], rate: float) -> Dict[str, Any]:
    """
    Calculate Net Present Value (NPV).
    
    Args:
        cashflows: List of cash flows (first value is typically initial investment, negative)
        rate: Discount rate (as decimal, e.g., 0.10 for 10%)
    
    Returns:
        Dictionary with npv value and status
    """
    if not cashflows:
        return {"error": "Cashflows list cannot be empty", "status": "error"}
    
    if rate <= -1:
        return {"error": "Rate must be greater than -1", "status": "error"}
    
    try:
        # Manual NPV calculation: sum of discounted cash flows
        npv_value = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))
        return {
            "npv": float(npv_value),
            "cashflows": cashflows,
            "rate": rate,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def irr(cashflows: List[float]) -> Dict[str, Any]:
    """
    Calculate Internal Rate of Return (IRR) using Newton-Raphson method.
    
    Args:
        cashflows: List of cash flows (first value is typically initial investment, negative)
    
    Returns:
        Dictionary with irr value and status
    """
    if not cashflows:
        return {"error": "Cashflows list cannot be empty", "status": "error"}
    
    if len(cashflows) < 2:
        return {"error": "At least 2 cashflows required for IRR calculation", "status": "error"}
    
    try:
        # Newton-Raphson method to find IRR
        # NPV = 0 at IRR, so we solve for rate where NPV = 0
        def npv_func(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))
        
        def npv_derivative(rate):
            return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cashflows) if i > 0)
        
        # Initial guess
        rate = 0.1
        tolerance = 1e-10
        max_iterations = 1000
        
        for _ in range(max_iterations):
            npv_val = npv_func(rate)
            if abs(npv_val) < tolerance:
                break
            
            deriv = npv_derivative(rate)
            if abs(deriv) < 1e-15:
                # Derivative too small, try bisection fallback
                break
            
            rate = rate - npv_val / deriv
            
            # Keep rate in reasonable bounds
            if rate <= -0.9999:
                rate = -0.9999
            if rate > 10:
                rate = 10
        
        # Verify the result
        final_npv = npv_func(rate)
        if abs(final_npv) > 1:  # If we couldn't converge well
            # Fallback: binary search
            low, high = -0.9999, 10.0
            for _ in range(100):
                mid = (low + high) / 2
                val = npv_func(mid)
                if abs(val) < tolerance:
                    rate = mid
                    break
                if val > 0:
                    low = mid
                else:
                    high = mid
        
        return {
            "irr": float(rate),
            "irr_percentage": float(rate * 100),
            "cashflows": cashflows,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def roi(gain: float, cost: float) -> Dict[str, Any]:
    """
    Calculate Return on Investment (ROI).
    
    Args:
        gain: Total gain from investment
        cost: Total cost of investment
    
    Returns:
        Dictionary with roi value and status
    """
    if cost == 0:
        return {"error": "Cost cannot be zero (division by zero)", "status": "error"}
    
    try:
        roi_value = (gain - cost) / cost
        return {
            "roi": float(roi_value),
            "roi_percentage": float(roi_value * 100),
            "gain": gain,
            "cost": cost,
            "net_profit": float(gain - cost),
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def break_even(fixed_cost: float, price: float, variable_cost: float) -> Dict[str, Any]:
    """
    Calculate Break-Even Point (units and revenue).
    
    Args:
        fixed_cost: Total fixed costs
        price: Selling price per unit
        variable_cost: Variable cost per unit
    
    Returns:
        Dictionary with break-even point and status
    """
    if price <= variable_cost:
        return {
            "error": "Price must be greater than variable cost for break-even",
            "status": "error"
        }
    
    if fixed_cost < 0:
        return {"error": "Fixed cost cannot be negative", "status": "error"}
    
    try:
        contribution_margin = price - variable_cost
        break_even_units = fixed_cost / contribution_margin
        break_even_revenue = break_even_units * price
        
        return {
            "break_even_units": float(break_even_units),
            "break_even_revenue": float(break_even_revenue),
            "contribution_margin": float(contribution_margin),
            "fixed_cost": fixed_cost,
            "price": price,
            "variable_cost": variable_cost,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def financial_ratios(
    balance_sheet: Dict[str, float],
    income_statement: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate key financial ratios from balance sheet and income statement.
    
    Args:
        balance_sheet: Dictionary containing:
            - current_assets, current_liabilities
            - total_assets, total_liabilities, shareholders_equity
            - cash, accounts_receivable, inventory (optional)
        income_statement: Dictionary containing:
            - revenue, net_income
            - cost_of_goods_sold (optional)
            - operating_expenses (optional)
    
    Returns:
        Dictionary with calculated ratios and status
    """
    try:
        ratios = {}
        
        # Liquidity Ratios
        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 1)
        
        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities
        else:
            ratios["current_ratio"] = None
            
        # Quick Ratio
        cash = balance_sheet.get("cash", 0)
        accounts_receivable = balance_sheet.get("accounts_receivable", 0)
        if current_liabilities > 0:
            ratios["quick_ratio"] = (cash + accounts_receivable) / current_liabilities
        else:
            ratios["quick_ratio"] = None
        
        # Leverage Ratios
        total_assets = balance_sheet.get("total_assets", 1)
        total_liabilities = balance_sheet.get("total_liabilities", 0)
        shareholders_equity = balance_sheet.get("shareholders_equity", 1)
        
        if total_assets > 0:
            ratios["debt_to_assets"] = total_liabilities / total_assets
            ratios["equity_ratio"] = shareholders_equity / total_assets
        else:
            ratios["debt_to_assets"] = None
            ratios["equity_ratio"] = None
            
        if shareholders_equity > 0:
            ratios["debt_to_equity"] = total_liabilities / shareholders_equity
        else:
            ratios["debt_to_equity"] = None
        
        # Profitability Ratios
        revenue = income_statement.get("revenue", 1)
        net_income = income_statement.get("net_income", 0)
        
        if revenue > 0:
            ratios["profit_margin"] = net_income / revenue
            ratios["return_on_assets"] = net_income / total_assets if total_assets > 0 else None
            ratios["return_on_equity"] = net_income / shareholders_equity if shareholders_equity > 0 else None
        else:
            ratios["profit_margin"] = None
            ratios["return_on_assets"] = None
            ratios["return_on_equity"] = None
        
        # Efficiency Ratios
        cost_of_goods_sold = income_statement.get("cost_of_goods_sold", 0)
        inventory = balance_sheet.get("inventory", 0)
        
        if inventory > 0 and cost_of_goods_sold > 0:
            ratios["inventory_turnover"] = cost_of_goods_sold / inventory
        else:
            ratios["inventory_turnover"] = None
        
        accounts_receivable = balance_sheet.get("accounts_receivable", 0)
        if accounts_receivable > 0 and revenue > 0:
            ratios["receivables_turnover"] = revenue / accounts_receivable
        else:
            ratios["receivables_turnover"] = None
        
        return {
            "ratios": ratios,
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


# Tool registry for the orchestration system
TOOLS_REGISTRY = {
    "npv": {
        "function": npv,
        "description": "Calculate Net Present Value of cash flows",
        "parameters": {
            "cashflows": "List of cash flows (initial investment first, then periodic cash flows)",
            "rate": "Discount rate as decimal (e.g., 0.10 for 10%)"
        }
    },
    "irr": {
        "function": irr,
        "description": "Calculate Internal Rate of Return",
        "parameters": {
            "cashflows": "List of cash flows (initial investment first, then periodic cash flows)"
        }
    },
    "roi": {
        "function": roi,
        "description": "Calculate Return on Investment",
        "parameters": {
            "gain": "Total gain from investment",
            "cost": "Total cost of investment"
        }
    },
    "break_even": {
        "function": break_even,
        "description": "Calculate Break-Even Point in units and revenue",
        "parameters": {
            "fixed_cost": "Total fixed costs",
            "price": "Selling price per unit",
            "variable_cost": "Variable cost per unit"
        }
    },
    "financial_ratios": {
        "function": financial_ratios,
        "description": "Calculate financial ratios from balance sheet and income statement",
        "parameters": {
            "balance_sheet": "Dictionary with balance sheet items",
            "income_statement": "Dictionary with income statement items"
        }
    }
}


def get_available_tools() -> Dict[str, Any]:
    """Return available tools with their descriptions and parameters."""
    return {
        tool_name: {
            "description": info["description"],
            "parameters": info["parameters"]
        }
        for tool_name, info in TOOLS_REGISTRY.items()
    }


def execute_tool(tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with given inputs.
    
    Args:
        tool_name: Name of the tool to execute
        inputs: Dictionary of input parameters
    
    Returns:
        Result from the tool execution
    """
    if tool_name not in TOOLS_REGISTRY:
        return {
            "error": f"Unknown tool: {tool_name}",
            "status": "error",
            "available_tools": list(TOOLS_REGISTRY.keys())
        }
    
    try:
        func = TOOLS_REGISTRY[tool_name]["function"]
        return func(**inputs)
    except TypeError as e:
        return {"error": f"Invalid parameters: {str(e)}", "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}
