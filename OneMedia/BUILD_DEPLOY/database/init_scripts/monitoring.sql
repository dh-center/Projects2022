drop table if exists stat;
create table stat
(
    source       text not null,
    channel_name text not null,
    event_name   text not null,
    count        int default 1,
    created_time timestamp without time zone default current_timestamp
);
drop index if exists stat_base_indx;
create index stat_base_indx on stat (source, channel_name, event_name);
create index stat_created_time_indx on stat (created_time);
create index stat_channel_name_indx on stat (channel_name);

drop table if exists stat_alive;
create table stat_alive
(
    app_name    text not null primary key,
    update_time timestamp without time zone default current_timestamp,
    msg         text
);

-- populate
insert into stat_alive (app_name, update_time, msg)
values ('VK_EXTRACTOR', '1000-01-01', 'DEAD');
insert into stat_alive (app_name, update_time, msg)
values ('WEB_CRAWLER', '1000-01-01', 'DEAD');
insert into stat_alive (app_name, update_time, msg)
values ('TLG_EXTRACTOR', '1000-01-01', 'DEAD');
