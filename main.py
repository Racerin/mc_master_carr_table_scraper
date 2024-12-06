import lib
import click


@click.group()
@click.option('--save-file-name', default=lib.MyTable.save_file_name, help="Filename to save as.")
@click.option('--save-file-separator', default=lib.MyTable.save_file_separator, help="Separator character between each column of data.")
def cli(mytable:lib.MyTable, save_file_name, save_file_separator):
    myTable = lib.MyTable(
        save_file_name=save_file_name, 
        save_file_separator=save_file_separator
        )
    mytable = myTable
    
@cli.command()
def get_table_from_html_file(mytable):
    mytable.get_table_from_file()

@cli.command()
@click.argument("--webpage")
def get_table_from_webpage(mytable, webpage):
    mytable.webpage_url=webpage
    mytable.get_table_from_webpage()

if __name__ == "__main__":
    cli()
