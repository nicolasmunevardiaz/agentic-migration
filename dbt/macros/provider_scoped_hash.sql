{% macro provider_scoped_hash(provider_expr, value_expr) -%}
md5(coalesce({{ provider_expr }}::text, '') || '|' || coalesce({{ value_expr }}::text, ''))
{%- endmacro %}
