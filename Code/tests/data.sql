INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, author_id, created)
VALUES
    ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

INSERT INTO block (tx_hash, block_no, date, comment, satname, satid, longitude, latitude, 
elevation, azimuth, timestamp)
VALUES
    ('0x6bf64c62038ff0d6123c828c0aac00bafa07bb090162a56128fda9a18506a291', 149, '23/04/2021 12:49:50'
    , 'testing', 'ISS', '56748', '53.48095', '-2.23743', '20', '145.33', '1521354419')