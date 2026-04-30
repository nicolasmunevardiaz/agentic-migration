select *
from {{ ref('coverage_period_fact') }}
where has_coverage_start_date <> (coverage_start_date is not null)
   or has_coverage_end_date <> (coverage_end_date is not null)
   or is_open_ended_period <> (coverage_start_date is not null and coverage_end_date is null)
   or is_end_date_only_period <> (coverage_start_date is null and coverage_end_date is not null)
   or is_undated_period <> (coverage_start_date is null and coverage_end_date is null)
   or has_inverted_date_range <> (
       coverage_start_date is not null
       and coverage_end_date is not null
       and coverage_end_date < coverage_start_date
   )
