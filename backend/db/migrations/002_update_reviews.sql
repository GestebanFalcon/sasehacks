ALTER TABLE reviews ADD COLUMN review_time TIMESTAMP NOT NULL;
ALTER TABLE reviews ADD COLUMN rating DOUBLE PRECISION NOT NULL;
ALTER TABLE reviews ADD COLUMN account_id BIGINT NOT NULL;

CREATE TYPE message_role AS ENUM ('user', 'assistant');
ALTER TABLE messages ADD COLUMN role message_role NOT NULL;


-- not sure if this is bad practice not making it the primary key.....