with macro_checks as (
    select
        {{ dq_normalize_code_token("'BDT-34'") }} = 'BDT_34' as passed,
        'dq_normalize_code_token hyphen' as check_name

    union all

    select
        {{ dq_normalize_code_token("' BDT_124 '") }} = 'BDT_124',
        'dq_normalize_code_token whitespace'

    union all

    select
        {{ dq_normalize_code_token("'med code.01'") }} = 'MED_CODE_01',
        'dq_normalize_code_token punctuation'

    union all

    select
        {{ dq_reference_final_segment("'Patient/abc-123'") }} = 'abc-123',
        'dq_reference_final_segment slash'

    union all

    select
        {{ dq_parse_status("null") }} = 'missing',
        'dq_parse_status missing'

    union all

    select
        {{ dq_parse_status("'2025-01-01'") }} = 'parsed',
        'dq_parse_status parsed'

    union all

    select
        {{ dq_timezone_status("null") }} = 'timezone_pending',
        'dq_timezone_status pending'

    union all

    select
        {{ dq_timezone_status("'America/New_York'") }} = 'timezone_approved',
        'dq_timezone_status approved'
)

select check_name
from macro_checks
where not passed
