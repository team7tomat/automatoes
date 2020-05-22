--
-- Create database tomato
--
CREATE DATABASE IF NOT EXISTS tomato;

USE tomato;

--
-- Create user
--
CREATE USER IF NOT EXISTS 'user'@'%' IDENTIFIED WITH mysql_native_password BY 'pass';

--
-- Grant privileges to user
--
GRANT ALL PRIVILEGES ON tomato.* TO 'user'@'%';
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'pass';

-- Show stuff
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'user'@'%';