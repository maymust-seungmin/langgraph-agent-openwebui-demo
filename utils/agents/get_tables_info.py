from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, inspect


load_dotenv()


def get_tables_info():
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    connection_string = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    engine = create_engine(connection_string)

    try:
        with engine.connect():
            inspector = inspect(engine)

            markdown_output = "# Database Schema Information\n\n"
            tables = inspector.get_table_names()
            markdown_output += "## Tables in the Database\n"

            if tables:
                markdown_output += "- " + "\n- ".join(tables) + "\n"
            else:
                markdown_output += "No tables found in the database.\n"

            for table_name in tables:
                markdown_output += f"\n## Table: {table_name}\n"
                # Get column information
                columns = inspector.get_columns(table_name)
                markdown_output += "### Columns\n"
                if columns:
                    markdown_output += (
                        "| Column Name | Data Type | Nullable | Default Value |\n"
                    )
                    markdown_output += (
                        "|-------------|-----------|----------|---------------|\n"
                    )
                    for column in columns:
                        markdown_output += f"| {column['name']} | {column['type']} | {column['nullable']} | {column.get('default', 'None')} |\n"
                else:
                    markdown_output += "No columns found.\n"
                # Get primary key information
                pk_constraint = inspector.get_pk_constraint(table_name)
                markdown_output += "\n### Primary Keys\n"
                primary_keys = pk_constraint.get("constrained_columns", [])
                markdown_output += (
                    f"- {', '.join(primary_keys) if primary_keys else 'None'}\n"
                )
                # Get foreign key information
                foreign_keys = inspector.get_foreign_keys(table_name)
                markdown_output += "\n### Foreign Keys\n"
                if foreign_keys:
                    for fk in foreign_keys:
                        markdown_output += f"- Constrained Columns: {', '.join(fk['constrained_columns'])}\n"
                        markdown_output += f"  Referred Table: {fk['referred_table']}\n"
                        markdown_output += (
                            f"  Referred Columns: {', '.join(fk['referred_columns'])}\n"
                        )
                else:
                    markdown_output += "- None\n"
                # Get index information
                indexes = inspector.get_indexes(table_name)
                markdown_output += "\n### Indexes\n"
                if indexes:
                    for index in indexes:
                        markdown_output += f"- Name: {index['name']}\n"
                        markdown_output += (
                            f"  Columns: {', '.join(index['column_names'])}\n"
                        )
                        markdown_output += f"  Unique: {index['unique']}\n"
                else:
                    markdown_output += "- None\n"

            return markdown_output
    finally:
        engine.dispose()


if __name__ == "__main__":
    result = get_tables_info()
    print(result)
