import lib
import click


@click.group(help="Meh")
@click.option('--save-file-name', default=lib.MyTable.save_file_name, help="Filename to save as. Include the file extension (.csv, .tsv, .txt, etc)")
@click.option('--save-file-separator', default=lib.MyTable.save_file_separator, help="Separator character between each column of data. Default '{}'".format(lib.MyTable.save_file_separator))
@click.pass_context
def cli(ctx:dict, save_file_name, save_file_separator):
    myTable = lib.MyTable(
        save_file_name=save_file_name, 
        save_file_separator=save_file_separator
        )
    ctx.ensure_object(dict)
    ctx.obj['mytable']=myTable
    # mytable = myTable
    
@cli.command()
@click.pass_context
@click.argument("html-file-name")
def get_table_from_html_file(ctx, html_file_name):
    mytable : lib.MyTable = ctx.obj['mytable']
    mytable.html_file_path = html_file_name
    mytable.get_table_from_file()

@cli.command()
@click.pass_context
@click.argument("webpage")
def get_table_from_webpage(ctx, webpage):
    mytable = ctx.obj['mytable']
    mytable.webpage_url=webpage
    mytable.get_table_from_webpage()

if __name__ == "__main__":
    cli()
