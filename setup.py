from setuptools import setup, find_packages

setup(
    name="kth-assistant",
    version="1.0",
    description="A repository for the code used in my master's thesis",
    author="Ludwig Kristoffersson",
    author_email="ludwig@kristoffersson.org",
    python_requires=">=3.11",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            'migration_create = db.migrations:create_migration',
            'migrate_up = db.migrations:run_migrations',
            'migrate_down = db.migrations:rollback',
            'llm_worker = commands.llm_worker:sync_main',
            'compute_faq = commands.compute_faq:sync_main'
        ]
    },
    tests_require=[],
)
