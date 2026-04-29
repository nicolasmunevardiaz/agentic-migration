In a value-based care world the payer doesn't just pay claims — it tracks outcomes, risk, and cost efficiency across the provider network. Several questions below ask you to adopt that payer lens: compare what providers report against what the payer sees, and surface the kind of insights a VBC analytics team would need.

Answer these eleven core questions using your analytics-ready tables. Deliver methodology and results as required (40 % data fidelity). Each question should be answerable with SQL: WHERE, JOIN, GROUP BY, COUNT, and date functions.

Five optional questions are included at the end that leverage coverage period and coverage status features for deeper analysis of enrollment patterns and coverage gaps.

Member overlap and attribution: How many active patients does each source (provider and payer) have in Gold? Which members appear in both provider and payer records? From the payer's perspective, which provider sees the most of its attributed members — and are there members the payer knows about that no provider reported? Additional: Of members found in both provider and payer records: what % had enrollment gaps (multiple coverage periods in payer data)? Which provider treats the highest % of members not found in payer enrollment data (uninsured)?

Gender distribution: What is the gender distribution (e.g. M / F) as counts or percentage of patients? Is it consistent across sources or are there discrepancies between what providers report and what the payer has on file?

Risk-stratified age groups: After normalizing dates of birth, how many patients fall into each age group (e.g. 0–17, 18–39, 40–64, 65+)? How did you handle invalid or missing dates? From the payer's standpoint, which age band concentrates the highest total cost and the highest per-member cost — and does that ranking hold across all providers?

Total cost of care (TCOC) per member: What are the mean, median, and 90th percentile of total cost per patient — combining medical and pharmacy claims — by provider and across the payer's full book? How does each provider's per-member cost compare to the network average the payer would benchmark against? Additional: Split cost analysis by visit coverage status from the COVERAGE_STATUS field: COVERED vs OUT_OF_COVERAGE vs UNINSURED visits. Compare average cost per member: those with continuous enrollment (single coverage period) vs interrupted enrollment (gaps). What % of total spending occurs on visits marked OUT_OF_COVERAGE?

Most prevalent conditions: Which diagnosis or condition appears most frequently in your analytics layer? How did you reconcile the different diagnostic coding systems used by each source?

Medications per patient: What distinct medications has each patient received (from your analytics-ready pharmacy facts)? How did you unify the different product codes used by each source?

Condition catalog: What is the full list of conditions you modeled in your analytics layer (unified diagnostic code + description)? How did you map the different codes used by each source to a single catalog? How many fact rows correspond to each entry?

Medication catalog: What is the full list of medications in your analytics layer (unified product identifier + name)? How did you reconcile the different pharmaceutical product codes across sources?

Treatment pattern alignment: For each condition in your diagnosis dimension, which medications appear associated (e.g. claims in the same encounter or with the same diagnostic reference)? From a VBC lens: do all providers prescribe a similar medication mix for the same condition, or does the payer's claims data reveal variation in treatment patterns? What is your association rule and how would it feed a therapeutic-adherence or formulary-compliance review? Additional: Do prescribed medications differ between COVERED and OUT_OF_COVERAGE visits for the same condition? For members with enrollment gaps: compare medication patterns during coverage vs outside coverage windows.

Vital signs (observations): After parsing the vitals JSON in your analytics layer (e.g. height in cm, weight in kg, systolic pressure from blood_pressure), report descriptive statistics for those three measures — by source and overall. Include at least mean and median, and add additional statistics you can justify (e.g. standard deviation, sample size, percentiles).

Unit-price benchmarking across the network: Using your normalized medication data for the catalog base price and final analytics layer order/claims rows for the observed unit price, build a reference table comparing base vs observed by provider. The payer uses this view to identify which providers bill above or below the network benchmark. What pattern do you observe? How would this analysis support a VBC contract negotiation or shared-savings reconciliation?

Additional analysis: Compare medication unit prices charged to members with different coverage status (from COVERAGE_STATUS in encounters). Do providers charge different base prices depending on whether a member is marked as UNINSURED vs COVERED? Identify providers with the largest price difference between insured and uninsured members.

