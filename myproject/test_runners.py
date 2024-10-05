from django.test.runner import DiscoverRunner
from django.db import connections

class MigrationTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)
        connections.close_all()
        for alias in connections.databases:
            connection = connections[alias]
            connection.prepare_database()
        return result