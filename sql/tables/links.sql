create table if not exists `links` (
    `id` integer primary key AUTOINCREMENT,
    `source_url` varchar(256) NOT NULL,
    `link` varchar(512) unique NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL
);
