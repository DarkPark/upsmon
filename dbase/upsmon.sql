CREATE TABLE "checks" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "time_start" INTEGER NOT NULL,
    "time_end" INTEGER
);
CREATE TABLE "options" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR NOT NULL
);
CREATE TABLE "values" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "id_option" INTEGER NOT NULL,
    "id_check" INTEGER NOT NULL,
    "value" REAL
);


insert into "options" ("name") values ("battery.charge");
insert into "options" ("name") values ("battery.voltage");
insert into "options" ("name") values ("battery.voltage.nominal");
insert into "options" ("name") values ("input.frequency");
insert into "options" ("name") values ("input.frequency.nominal");
insert into "options" ("name") values ("input.voltage");
insert into "options" ("name") values ("input.voltage.fault");
insert into "options" ("name") values ("input.voltage.nominal");
insert into "options" ("name") values ("output.voltage");
insert into "options" ("name") values ("ups.beeper.status");
insert into "options" ("name") values ("ups.load");
insert into "options" ("name") values ("ups.status");
insert into "options" ("name") values ("ups.temperature");