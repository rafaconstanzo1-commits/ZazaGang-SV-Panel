def migrate(migrator, database, **kwargs):
    database.execute_sql(
        "UPDATE crafty_settings SET og_color = ? WHERE og_color = ?",
        ("#4d892d", "#005cd1"),
    )


def rollback(migrator, database, **kwargs):
    database.execute_sql(
        "UPDATE crafty_settings SET og_color = ? WHERE og_color = ?",
        ("#005cd1", "#4d892d"),
    )
