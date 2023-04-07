CREATE TABLE chat_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    count INTEGER NOT NULL,
    max_uses INTEGER NOT NULL
);