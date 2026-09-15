-- Yearly performance trend
SELECT
    YEAR(review_date) AS review_year,
    ROUND(AVG(performance_score), 2) AS avg_score
FROM hr_analytics_oltp.reviews
GROUP BY YEAR(review_date)
ORDER BY review_year;

-- Top performers by department using window function
SELECT
    department,
    employee_id,
    performance_score,
    DENSE_RANK() OVER (
        PARTITION BY department
        ORDER BY performance_score DESC
    ) AS dept_rank
FROM hr_analytics_oltp.reviews
ORDER BY department, dept_rank;

-- Employee historical SCD Type 2 snapshot
SELECT
    employee_id,
    employee_name,
    department,
    role,
    salary,
    start_date,
    end_date,
    is_current
FROM hr_analytics_warehouse.dim_employee
WHERE business_key = 1
ORDER BY start_date;
