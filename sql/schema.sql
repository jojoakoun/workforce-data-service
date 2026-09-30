DROP TABLE IF EXISTS workforce_records;
DROP TABLE IF EXISTS departments;


CREATE TABLE departments (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    long_name_en TEXT NOT NULL UNIQUE,
    long_name_fr TEXT NOT NULL,
    short_name_en TEXT,
    short_name_fr TEXT
);


CREATE TABLE workforce_records (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    period DATE NOT NULL,
    source TEXT NOT NULL,
    department_id INTEGER NOT NULL
        REFERENCES departments(id),
    tenure TEXT,
    headcount INTEGER,
    fte NUMERIC,

    CHECK (headcount IS NULL OR headcount >= 0),
    CHECK (fte IS NULL OR fte >= 0),

    UNIQUE NULLS NOT DISTINCT (
        period,
        source,
        department_id,
        tenure
    )
);