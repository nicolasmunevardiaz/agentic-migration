{% macro dq_trimmed_text(value_expr) -%}
nullif(btrim({{ value_expr }}::text), '')
{%- endmacro %}

{% macro dq_clean_wrapped_text(value_expr) -%}
nullif(
    btrim(
        regexp_replace(
            regexp_replace(btrim(coalesce({{ value_expr }}::text, '')), '^"+|"+$', '', 'g'),
            '^''+|''+$',
            '',
            'g'
        )
    ),
    ''
)
{%- endmacro %}

{% macro dq_normalize_code_token(value_expr) -%}
nullif(
    btrim(
        regexp_replace(
            regexp_replace(upper(coalesce({{ value_expr }}::text, '')), '[^A-Z0-9]+', '_', 'g'),
            '^_+|_+$',
            '',
            'g'
        )
    ),
    ''
)
{%- endmacro %}

{% macro dq_reference_final_segment(value_expr) -%}
nullif(regexp_replace(btrim(coalesce({{ value_expr }}::text, '')), '^.*/', ''), '')
{%- endmacro %}

{% macro dq_provider_scoped_reference_key(provider_expr, reference_expr) -%}
{{ provider_scoped_hash(provider_expr, dq_reference_final_segment(reference_expr)) }}
{%- endmacro %}

{% macro dq_parse_status(value_expr) -%}
case
    when {{ value_expr }} is null then 'missing'
    else 'parsed'
end
{%- endmacro %}

{% macro dq_timezone_status(timezone_expr) -%}
case
    when {{ timezone_expr }} is null then 'timezone_pending'
    else 'timezone_approved'
end
{%- endmacro %}

{% macro dq_temporal_has_explicit_offset(value_expr) -%}
coalesce(
    {{ value_expr }}::text ~* '([0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?(Z|[+-][0-9]{2}(:?[0-9]{2})?)$)',
    false
)
{%- endmacro %}
