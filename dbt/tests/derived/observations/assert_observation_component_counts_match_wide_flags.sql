with wide as (
    select
        observation_source_row_id,
        (has_payload_height::integer
            + has_payload_weight::integer
            + case when systolic_bp is not null then 1 else 0 end
            + case when diastolic_bp is not null then 1 else 0 end
            + has_payload_pulse::integer
            + has_payload_temperature::integer
            + has_payload_bmi::integer) as expected_component_count
    from {{ ref('observation_vitals_wide') }}
),

component_counts as (
    select
        observation_source_row_id,
        count(*) as actual_component_count
    from {{ ref('observation_vital_components') }}
    group by observation_source_row_id
)

select
    wide.observation_source_row_id,
    wide.expected_component_count,
    coalesce(component_counts.actual_component_count, 0) as actual_component_count
from wide
left join component_counts using (observation_source_row_id)
where wide.expected_component_count <> coalesce(component_counts.actual_component_count, 0)
