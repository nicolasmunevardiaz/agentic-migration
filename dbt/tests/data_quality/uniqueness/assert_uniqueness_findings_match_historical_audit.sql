select *
from {{ ref('dq_uniqueness_coverage_period_metrics') }}
where (
    provider_slug = 'data_provider_1_aegis_care_network'
    and duplicate_key_rows <> 4686
) or (
    provider_slug = 'data_provider_2_bluestone_health'
    and duplicate_key_rows <> 233
) or (
    provider_slug = 'data_provider_3_northcare_clinics'
    and duplicate_key_rows <> 2983
) or (
    provider_slug = 'data_provider_4_valleybridge_medical'
    and duplicate_key_rows <> 5766
) or (
    provider_slug = 'data_provider_5_pacific_shield_insurance'
    and duplicate_key_rows <> 21155
)
