import peewee


def migrate(migrator, database, **kwargs):
    migrator.add_columns(
        "users",
        server_port=peewee.IntegerField(default=25565),
    )


def rollback(migrator, database, **kwargs):
    migrator.drop_columns("users", ["server_port"])
