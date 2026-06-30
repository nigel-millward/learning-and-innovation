/*
  Transformation: Macro Reuse (apply shared logic)
  ------------------------------------------------
  This model carries no new SQL idea of its own — it demonstrates calling the
  project macros so a transformation rule lives in one place. canonicalise_string
  applies the same trim/lower/blank-to-NULL rule used wherever text is
  standardised; safe_divide guards every ratio against a zero denominator. Change
  the rule in the macro and every caller updates at once.

  When to use it: whenever the same expression would otherwise be copy-pasted
  across models. Centralising it in a macro removes drift between models and
  makes the intent self-documenting at the call site.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    -- Shared canonicalisation rule, applied via macro
    {{ canonicalise_string('BROWSER') }} AS browser_clean,
    {{ canonicalise_string('DEVICE_TYPE') }} AS device_type_clean,
    -- Pages per second, guarded against a zero/NULL duration via macro
    {{ safe_divide(
        'TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0))',
        'TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))'
    ) }} AS pages_per_second
FROM {{ source('studios_piano', 'studios_piano_events') }}
