from sqlalchemy import create_engine, MetaData

# Replace 'your_database.db' with your actual SQLite database file
database_path = 'sqlite:///people.sqlite'
engine = create_engine(database_path)
metadata = MetaData()

# Reflect the tables in the database
metadata.reflect(bind=engine)

# Iterate over all tables and print their descriptions
for table_name in metadata.tables:
    print(f"Table: {table_name}")
    table = metadata.tables[table_name]

    # Iterate over columns in the table and print details
    for column in table.c:
        print(f"Column: {column.name}")
        print(f"Type: {column.type}")
        print(f"Nullable: {column.nullable}")
        print(f"Primary Key: {column.primary_key}")
        print(f"---------------------")

    print(f"{'='*20}\n")