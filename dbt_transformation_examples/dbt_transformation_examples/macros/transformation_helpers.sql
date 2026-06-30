/*
  Macros: reusable transformation logic (DRY)
  -------------------------------------------
  A macro is a Jinja function that returns a SQL fragment, letting a
  transformation be defined once and reused across models. This keeps a rule —
  here "how we canonicalise a string" and "how we divide safely" — consistent
  everywhere instead of being re-typed (and re-bugged) per model. Macros are
  dbt's answer to copy-paste SQL; dbt_utils ships many ready-made ones
  (generate_surrogate_key, star, date_spine).
*/

-- Canonicalise free text the same way everywhere: trimmed, lower-cased, blanks -> NULL
{% macro canonicalise_string(column) %}
    NULLIF(LOWER(TRIM({{ column }})), '')
{% endmacro %}

-- Divide without raising on a zero denominator (returns NULL instead)
{% macro safe_divide(numerator, denominator) %}
    {{ numerator }} / NULLIF({{ denominator }}, 0)
{% endmacro %}
