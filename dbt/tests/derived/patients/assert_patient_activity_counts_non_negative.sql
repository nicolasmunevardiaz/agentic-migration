select *
from {{ ref('patient_transaction_activity') }}
where coverage_rows < 0
   or encounter_rows < 0
   or condition_rows < 0
   or medication_rows < 0
   or observation_rows < 0
   or observation_payload_rows < 0
   or cost_rows < 0
   or transactional_row_count < 0
   or clinical_transaction_row_count < 0
   or financial_transaction_row_count < 0
