PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('9a01765dab91');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(64) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(256), about_me VARCHAR(140), last_seen DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);
INSERT INTO user VALUES(1,'sakhi','sakhi@tesla.com','scrypt:32768:8:1$bYLMR0o2fBgjVLoQ$0451ad460c02fff353b9adf17b5174dc2d7aabb38fade2a6132d478f34065e8c5ca4f7e1bc2d73962e3bd4b36930d732eb027cb841e5a9257309a5b55510ce87','I am new aspiring developer looking to improve my skills. Excited to see what Flask can do.','2024-12-05 08:32:11.636283');
INSERT INTO user VALUES(2,'xyz','musk@spacex.com','scrypt:32768:8:1$tCHp7GAkiT1eTvG2$664c7f6c57c34509fd31a3d2d7615d2782843a3a011f2c88ffd5870fa128fcd288287cd1945d10f491bb619d4dd7616f080c754d9196efe6146d9fb4817d9a2b','A businessman known for his key roles in the space company SpaceX and the automotive company Tesla, Inc. And owenership of X.','2024-11-24 13:08:19.575021');
INSERT INTO user VALUES(3,'zethe','zethe@something.com','scrypt:32768:8:1$sVNDfLfGEdvQ47rY$7fdd7fae9f54c435bc36700d579ff5ec68d107fe0372c4f8364c8928d5fddabf3c8cef71aad1bd42a0f7b962f31e3d6a18409ad307dd74ddaa4997697d5ffa34',NULL,'2024-12-05 08:29:03.914555');
INSERT INTO user VALUES(4,'zothi','zothi@meta.io','scrypt:32768:8:1$1KOPW4VXrPlVFdpW$8605558472a574975ae81ab03dab609c147a64cabc8c8d9989818f6a76aed45788ed5251d442a88161d6dbb9cbd07f9b7652bfe2bab68d85cc978a98cdecb24c',NULL,'2024-12-05 08:29:36.010665');
INSERT INTO user VALUES(5,'john','john@doe.unknown','scrypt:32768:8:1$VfYVwZU7wWUvMzTy$411e293655bfb7585b40cf06e6fe072d1b5c2a26bb95430fa58ecff426bd00842d60aa736da409af3c1389494a87e46dcf99aff8aa879468218a5ceb871676e0',NULL,'2024-12-05 08:30:23.915607');
CREATE TABLE post (
	id INTEGER NOT NULL, 
	body VARCHAR(140) NOT NULL, 
	timestamp DATETIME NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE IF NOT EXISTS "followers" (
	follower_id INTEGER NOT NULL, 
	followed_id INTEGER NOT NULL, 
	PRIMARY KEY (followed_id), 
	FOREIGN KEY(followed_id) REFERENCES user (id), 
	FOREIGN KEY(follower_id) REFERENCES user (id)
);
CREATE UNIQUE INDEX ix_user_email ON user (email);
CREATE INDEX ix_post_timestamp ON post (timestamp);
CREATE INDEX ix_post_user_id ON post (user_id);
COMMIT;
