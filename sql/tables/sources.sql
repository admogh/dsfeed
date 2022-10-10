create table if not exists `sources` (
    `id` integer primary key AUTOINCREMENT,
    `url` varchar(256) unique NOT NULL,
    `keyword` varchar(128) default "",
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL
);
