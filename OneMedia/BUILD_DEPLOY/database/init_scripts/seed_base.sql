-- TODO ADD CHANNEL NEWS VIEWS !!! Add that value to metric either
-- TODO ADD SYNTACTIC key, make back index to follow it, keep date in queue, and set where it's added
-- TODO ADD META information, pictures, video, photo
-- TODO ADD channel tracking information (number of subscribers, to estimate weights)


drop table if exists message;
create table message
(
    uid                bigserial unique not null,
    message_id         text,
    channel_id         text,
    channel_name       text,
    channel_title      text,
    sender_username    text,
    sender_id          text,
    publish_date       date,
    content            text             not null,
    source_id          text,
    forward_channel_id text,
    forward_message_id text,
    meta_image         text,
    created_time       timestamp without time zone default current_timestamp,
    primary key (message_id, channel_name)
);

create index date_channel_indx on message (channel_id, publish_date);
create index date_indx on message (publish_date);
create index created_date_indx on message (created_time);
create index uid_indx on message (uid);
create index tlg_channel_id_indx on message (channel_id);

drop table if exists ono_anchors;
create table ono_anchors
(
    chanel_name             text primary key,
    last_message_id         text               default 'NOT_SET',
    channel_id              text unique,
    channel_display_name    text,
    channel_type            text,
    system_mark             text,
    subscribers             int,
    subscribers_update_time timestamp not null default now()
);

create index tlg_ono_anchors_channel_id_indx on ono_anchors (channel_id);

drop table if exists web_message;
create table web_message
(
    uid          bigserial unique not null,
    message_id   serial,
    link         text,
    channel_name text             not null,
    sender_name  text,
    publish_date date,
    title        text             not null,
    content      text             not null,
    meta_image   text,
    html_page    text             not null,
    created_time timestamp without time zone default current_timestamp,
    primary key (link)
);

drop index if exists web_msg_channel_indx;
drop index if exists web_date_channel_indx;
drop index if exists web_date_indx;
drop index if exists channel_name_indx;
drop index if exists web_uid_indx;
create index web_msg_channel_indx on web_message (message_id, channel_name);
create index web_date_channel_indx on web_message (channel_name, publish_date);
create index web_date_indx on web_message (publish_date);
create index web_created_date_indx on web_message (created_time);
create index channel_name_indx on ono_anchors (chanel_name);
create index web_uid_indx on web_message (uid);

drop table if exists web_message_anchors;
create table web_message_anchors
(
    anchor       text,
    channel_name text,
    crawl_date   timestamp with time zone default current_timestamp,
    primary key (anchor, channel_name)
);
drop index if exists web_message_anchors_anchor_indx;
create index web_message_anchors_anchor_indx on web_message_anchors (anchor);

drop table if exists vk_message_anchors;
create table vk_message_anchors
(
    channel_name           text,
    channel_id             integer,
    screen_name            text,
    last_message_id        integer,
    participants           integer,
    last_time_updated_info timestamp default to_timestamp(0),
    is_group               bool      default true,
    primary key (channel_id)
);
create index vk_message_anchors_indx on vk_message_anchors (channel_id);

drop table if exists vk_message;
create table vk_message
(
    uid             bigserial unique not null,
    message_id      integer,
    owner_id        integer,
    from_id         integer,
    message_content text,
    publish_date    integer,
    meta_image      text,
    created_time    timestamp without time zone default current_timestamp,
    primary key (message_id, owner_id)
);

create index vk_uid_indx on vk_message (uid);
create index vk_message_owner_id_indx on vk_message (owner_id);
create index vk_created_date_indx on vk_message (created_time);

-- To share database access with other
-- ADD READ USER
create user read_user with password 'one_media_read';
grant connect on database postgres to read_user;
grant usage on schema public to read_user;
grant select on all tables in schema public to read_user;
