-- ==========================================
-- Load basket_analysis_results.csv into PostgreSQL
-- Run from the project root (Bi/ directory):
--   psql -d grocery_sales -f Dashboard\ Version/backend/scripts/load_basket_table.sql
--
-- Uses \copy (client-side) so the path is relative to where psql is run.
-- ==========================================

TRUNCATE TABLE basket_analysis_results;

\copy basket_analysis_results(product1, product2, basket_label, support, confidence_p1, confidence_p2, lift, support_pct, confidence_p1_pct, confidence_p2_pct, nb_transactions)
FROM 'data/csv_exports/basket_analysis_results.csv'
DELIMITER ','
CSV HEADER;

-- Verify load
SELECT COUNT(*) AS total_rules FROM basket_analysis_results;
SELECT MIN(lift) AS min_lift, MAX(lift) AS max_lift,
       MIN(support) AS min_support, MAX(support) AS max_support
FROM basket_analysis_results;
