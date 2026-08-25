import click


@click.command("hello-custom")
def hello_custom():
    """Print a message from the custom Bench CLI."""
    click.echo("Hello from the custom Bench CLI!")


@click.command("hello-app")
def hello_app():
    """Print a message from the hello-app command."""
    click.echo("Hello from custom command!")


commands = [
    hello_custom,
    hello_app
]