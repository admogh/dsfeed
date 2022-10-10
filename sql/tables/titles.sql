create table if not exists `titles` (
    `id` integer primary key AUTOINCREMENT,
    `source_url` varchar(256) NOT NULL,
    `title` varchar(512) unique NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL
);
