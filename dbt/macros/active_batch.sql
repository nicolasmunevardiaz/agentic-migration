{% macro active_batch_filter(alias=None) -%}
{%- if alias -%}
{{ alias }}.review_batch_id = '{{ var("review_batch_id", "plan-04-5-v0-2-fixtures") }}'
{%- else -%}
review_batch_id = '{{ var("review_batch_id", "plan-04-5-v0-2-fixtures") }}'
{%- endif -%}
{%- endmacro %}
