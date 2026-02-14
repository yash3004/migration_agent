Based on the schema analyses provided, here are the SQL migration scripts for the two tables: `raisers_edge_donors` to `salesforce_contact` and `instagram_contacts` to `whatsapp_contacts`. The scripts include the necessary transformations and considerations for data type compatibility, missing fields, and valid mappings.

### Migration Script for `raisers_edge_donors` to `salesforce_contact`

```sql
-- Migration script for raisers_edge_donors to salesforce_contact

-- Create the target table if it does not exist
CREATE TABLE IF NOT EXISTS salesforce_contact (
    id VARCHAR(18) PRIMARY KEY, -- donor_id converted to VARCHAR
    full_name VARCHAR(100),
    email VARCHAR(255),
    total_gifts DECIMAL(10,2),
    created_date DATETIME,
    donor_id INTEGER -- Optional: retain donor_id for reference
);

-- Insert data from the source table into the target table
INSERT INTO salesforce_contact (id, full_name, email, total_gifts, created_date, donor_id)
SELECT 
    CAST(donor_id AS VARCHAR(18)) AS id, -- Convert donor_id to VARCHAR
    CONCAT(donor_fname, ' ', donor_lname) AS full_name, -- Concatenate first and last names
    donor_email AS email,
    gift_total AS total_gifts,
    created_date AS created_date,
    donor_id -- Retain donor_id for reference
FROM raisers_edge_donors;
```

### Migration Script for `instagram_contacts` to `whatsapp_contacts`

```sql
-- Migration script for instagram_contacts to whatsapp_contacts

-- Create the target table if it does not exist
CREATE TABLE IF NOT EXISTS whatsapp_contacts (
    id VARCHAR(18) PRIMARY KEY, -- contact_id converted to VARCHAR
    full_name VARCHAR(100),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    last_message_date TIMESTAMP,
    contact_id INTEGER -- Optional: retain contact_id for reference
);

-- Insert data from the source table into the target table
INSERT INTO whatsapp_contacts (id, full_name, email, phone_number, last_message_date, contact_id)
SELECT 
    CAST(contact_id AS VARCHAR(18)) AS id, -- Convert contact_id to VARCHAR
    CONCAT(contact_fname, ' ', contact_lname) AS full_name, -- Concatenate first and last names
    contact_email AS email,
    mobile_number AS phone_number,
    created_date AS last_message_date, -- Map created_date to last_message_date
    contact_id -- Retain contact_id for reference
FROM instagram_contacts;
```

### Notes:
1. **Data Type Conversion**: The scripts convert `donor_id` and `contact_id` from INTEGER to VARCHAR(18) to match the target schema.
2. **Concatenation**: The scripts concatenate first and last names to create the `full_name` field.
3. **Optional Fields**: The original identifiers (`donor_id` and `contact_id`) are retained in the target tables for reference, which can be useful for tracking.
4. **Testing**: It is recommended to test these migration scripts in a development environment before executing them in production to ensure data integrity and correctness.