import peewee


def migrate(migrator, database, **kwargs):
    migrator.add_columns(
        "users",
        playit_address=peewee.CharField(default=""),
        server_ram_gb=peewee.FloatField(default=2.0),
    )


def rollback(migrator, database, **kwargs):
    migrator.drop_columns("users", ["playit_address", "server_ram_gb"])
