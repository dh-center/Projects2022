drop table if exists user_query cascade;
create table user_query
(
    uid          bigserial unique not null,
    user_id      int              not null,
    name         text             not null,
    query        json             not null,
    created_time timestamp        not null default now(),
    primary key (uid),
    unique (user_id, name)
);

drop index if exists user_query_user_id_indx;
create index user_query_user_id_indx on user_query (user_id);

drop table if exists user_subscription;
create table user_subscription
(
    uid          bigserial unique not null,
    user_id      int              not null,
    query_id     bigserial        not null references user_query on delete cascade,
    created_time timestamp        not null default now(),
    primary key (uid),
    unique (user_id, query_id)
);

drop index if exists user_subscription_user_id_indx;
create index user_subscription_user_id_indx on user_subscription (user_id);
drop index if exists user_subscription_query_id_indx;
create index user_subscription_query_id_indx on user_subscription (query_id);

drop table if exists user_info;
create table user_info
(
    uid     bigserial unique not null,
    user_id int              not null,
    name    text default null,
    login   text default null,
    phone   text default null,
    meta    json             not null,
    unique (user_id),
    primary key (uid)
);

drop index if exists user_info_user_id_indx;
create index user_info_user_id_indx on user_info (user_id);


drop table if exists user_action_log;
create table user_action_log
(
    uid          bigserial unique not null,
    user_id      int              not null,
    name         text             not null,
    created_time timestamp        not null default now(),
    data         json             not null,
    primary key (uid)
);

drop index if exists user_action_log_id_indx;
create index user_action_log_id_indx on user_action_log (user_id);

drop index if exists user_action_log_created_time_indx;
create index user_action_log_created_time_indx on user_action_log (created_time);

drop index if exists user_info_phone_indx;
create index user_info_phone_indx on user_info (phone);

drop table if exists user_support_request;
create table user_support_request
(
    uid           bigserial unique not null,
    user_id       int              not null,
    created_time  timestamp        not null default now(),
    is_solved     bool             not null default false,
    support_query json             not null,
    primary key (uid)
);

drop index if exists user_support_request_user_id_indx;
create index user_support_request_user_id_indx on user_support_request (user_id);

-- Implementation
drop table if exists notify_anchors;
create table notify_anchors
(
    source_type text      not null, -- VK, WEB, TLG
    last_uid    bigserial not null,
    primary key (source_type)
);

-- Always default before run
insert into notify_anchors (source_type, last_uid)
values ('VK', (select max(uid) from vk_message));
insert into notify_anchors (source_type, last_uid)
values ('WEB', (select max(uid) from web_message));
insert into notify_anchors (source_type, last_uid)
values ('TLG', (select max(uid) from message));