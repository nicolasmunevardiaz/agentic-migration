select *
from {{ ref('patient_transaction_activity') }}
where has_transactional_data <> (transactional_row_count > 0)
   or has_clinical_transactional_data <> (clinical_transaction_row_count > 0)
   or has_financial_transactional_data <> (financial_transaction_row_count > 0)
   or has_observation_payload <> (observation_payload_rows > 0)
