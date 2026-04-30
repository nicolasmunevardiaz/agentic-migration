{% macro normalize_gender_code(column_expr) -%}
nullif(regexp_replace(upper(trim(both '"' from btrim(coalesce({{ column_expr }}::text, '')))), '\s+', '', 'g'), '')
{%- endmacro %}
