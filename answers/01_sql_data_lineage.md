# SQL and Data Lineage

## Q1: Potential Issues with the Analyst's Changes

Looking at the changes the analyst made, there are a few things that 
concern me.

First, dropping `product_name` is risky. Even though `product_id` 
uniquely identifies a product, stakeholders and business users rely on 
readable names in dashboards and reports. A director doesn't want to 
see product ID 4821 — they want to see "Mountain Bike". Beyond that, 
any upstream pipelines still sending `product_name` in their payloads 
will now have nowhere to put that field, which could cause ingestion 
failures or silent data loss depending on how strict the pipeline is.

Second, splitting the `warehouse` column into `warehouse_letter` and 
`warehouse_num_id` introduces a subtle but serious bug risk. Storing 
the numeric part as an INT will silently strip leading zeros — so a 
warehouse like `W0123456` becomes `W123456` after recombination. That's 
a data corruption issue that's easy to miss until something downstream 
breaks. On top of that, any existing queries or ETL jobs that reference 
`warehouse` by name will fail immediately after this change.

---

## Q2: Did the Analyst Make Any Undocumented Changes?

Yes — the analyst changed `date_sold` and `date_manufactured` from 
`datetime` to `DATE` but never mentioned it in their report.

This is a quiet but breaking change. If the original data captured the 
time of day (e.g., `2024-08-23 14:32:00`), that information is now 
permanently gone. Any downstream logic that filters or sorts by time 
of day will either break or silently return wrong results. From a 
compliance standpoint, losing that timestamp could also be a problem 
if the business ever needs to audit when exactly a product was sold or 
manufactured.

---

## Q3: SQL Query to Recombine the Warehouse Columns

To reconstruct the original warehouse value, I'd use CONCAT along with 
LPAD to restore any leading zeros that were lost when the number was 
stored as an integer:
```sql
SELECT
  product_id,
  CONCAT(warehouse_letter, LPAD(CAST(warehouse_num_id AS VARCHAR), 7, '0')) AS warehouse,
  store,
  price,
  cost,
  date_sold,
  date_manufactured
FROM products;
```

The LPAD ensures the numeric part is always 7 digits, padding with 
zeros if needed. If leading zeros were never present in the original 
data this won't cause issues, but it's the safer assumption to make.

---

## Q4: How I'd Improve Data Lineage Tracking

The core problem here is that the analyst made changes based on their 
own assumptions without validating them against stakeholder needs or 
documenting the impact. A few things I'd put in place to prevent this:

Before any schema change happens, I'd want a lightweight review process 
— something like a PR description or a simple RFC that documents what's 
changing, why, and who downstream might be affected. Pairing that with 
a data catalog (dbt docs or Google Data Catalog work well for this) 
means every column has a documented owner and business meaning, so 
it's obvious who to loop in before making changes.

During changes, I'd use dbt to manage transformations. It gives you 
column-level lineage out of the box, so you can immediately see which 
models and dashboards are affected when you touch an upstream field. 
I'd also avoid hard-dropping or renaming columns right away — instead, 
deprecate them first and keep the old column around for a migration 
window so consumers have time to adapt.

After a change ships, automated data quality checks (Great Expectations 
or dbt tests) should validate that row counts, null rates, and value 
ranges are still within expected bounds. And a simple human-readable 
changelog that stakeholders can actually read goes a long way — it 
builds trust and keeps everyone on the same page.