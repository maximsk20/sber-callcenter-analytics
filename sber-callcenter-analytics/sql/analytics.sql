DROP TABLE IF EXISTS temp_recent_calls;

CREATE TEMP TABLE temp_recent_calls AS
SELECT
    call_id,
    operator_id,
    call_start,
    duration_sec,
    status,
    tags,
    csat_score
FROM calls_log
WHERE call_start >= CURRENT_DATE - INTERVAL '30 days';


WITH operator_performance AS (
SELECT
    operator_id,
    call_id,
    duration_sec,
    status,
    csat_score,

    ROW_NUMBER() OVER (
        PARTITION BY operator_id
        ORDER BY duration_sec DESC
    ) AS call_rank_by_duration,


    AVG(duration_sec) OVER (
        PARTITION BY operator_id
        ORDER BY call_start
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_duration,


    LAG(call_start) OVER (
        PARTITION BY operator_id
        ORDER BY call_start
    ) AS prev_call_start
FROM temp_recent_calls
),
aggregated_metrics AS (
    SELECT
        op.operator_id,
        o.department,
        o.grade,
        COUNT(op.call_id) AS total_handled_calls,
        COUNT(CASE WHEN op.duration_sec < 10 AND op.status = 'resolved' THEN 1 END) AS error_calls_count,
        ROUND(AVG(op.duration_sec), 2) AS mean_duration_sec,
ROUND(AVG(op.csat_score)::numeric, 2) AS mean_csat
    FROM operator_performance op
    LEFT JOIN operators o ON op.operator_id = o.operator_id
    GROUP BY op.operator_id, o.department, o.grade
)
SELECT
    operator_id,
    department,
    grade,
    total_handled_calls,
    error_calls_count,
    ROUND((error_calls_count::numeric / NULLIF(total_handled_calls, 0)) * 100, 2) AS error_percentage,
    mean_duration_sec,
    mean_csat
FROM aggregated_metrics
WHERE error_calls_count > 0
ORDER BY error_percentage DESC;