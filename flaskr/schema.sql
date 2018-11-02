drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);
drop table if exists doctors;

create table doctors (
  id integer primary key autoincrement,
  name text not null,
  startTime TIME not null,
  endTime TIME not null
);