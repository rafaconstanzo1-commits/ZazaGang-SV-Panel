def migrate(migrator, database, **kwargs):
    database.execute_sql("UPDATE users SET lang = ?", ("es_ES",))


def rollback(migrator, database, **kwargs):
    database.execute_sql("UPDATE users SET lang = ?", ("en_EN",))
