# test.py — corrected version
# Old (wrong):  generate_plan("John", 28, "Male", 600000, 2, 100000, "Mid Term")
# New (correct): generate_plan(28, "Male", 2, 600000, 100000, "Mid Term")

import sys
sys.path.insert(0, r"C:\Users\AARYAN MAYEKAR\KASHGROWW APP")

from recommend import generate_plan

result = generate_plan(
    investor_name = "John",
    age        = 28,
    gender     = "Male",
    number_of_dependents = 2,
    annual_income     = 600000,
    investment_amount     = 100000,
    horizon    = "Mid Term"
)

print(f"Predicted Risk level:     {result['risk_level']}")
print(f"Blended return: {result['blended_return']}%")
for item in result['plan']:
    print(f"  {item['asset_type']:<25} {item['allocation_pct']}%  Rs {item['amount_inr']:,.0f}")