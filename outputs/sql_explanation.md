# SQL Explanation

# SQL Migrations Audit Documentation

## Overview
This document provides an audit trail for the SQL migration scripts executed to transfer data from the `raisers_edge_donors` table to the `salesforce_contact` table, and from the `instagram_contacts` table to the `whatsapp_contacts` table. The purpose of these migrations is to ensure data integrity, compatibility, and proper mapping of fields between the source and target schemas.

## Migration Details

### 1. Migration from `raisers_edge_donors` to `salesforce_contact`

#### Migration Script
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

#### Key Considerations
- **Data Type Conversion**: The `donor_id` field is converted from INTEGER to VARCHAR(18) to align with the target schema requirements.
- **Field Mapping**: The `full_name` field is created by concatenating `donor_fname` and `donor_lname`, ensuring that the target schema has a complete name representation.
- **Optional Fields**: The original `donor_id` is retained in the `salesforce_contact` table for future reference, which aids in tracking and auditing.

### 2. Migration from `instagram_contacts` to `whatsapp_contacts`

#### Migration Script
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

#### Key Considerations
- **Data Type Conversion**: Similar to the previous migration, `contact_id` is converted from INTEGER to VARCHAR(18) to meet the target schema's requirements.
- **Field Mapping**: The `last_message_date` field is populated using the `created_date` from the source table, ensuring that relevant timestamps are preserved.
- **Optional Fields**: The original `contact_id` is also retained in the `whatsapp_contacts` table for reference purposes.

## Testing and Validation
- It is crucial to test these migration scripts in a development environment prior to executing them in production. This ensures that:
  - Data integrity is maintained.
  - All transformations and mappings are correctly applied.
  - No data loss occurs during the migration process.

## Conclusion
The provided SQL migration scripts have been designed with careful consideration of data types, field mappings, and optional references. This documentation serves as an audit trail for the migration process, ensuring transparency and accountability in data handling practices.