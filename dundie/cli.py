import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import User
from .models.user import generate_username

main = typer.Typer(name="dundie CLI", add_completion=False)


@main.command()
def shell() -> None:
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(
            argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list() -> None:
    """Lists all users"""
    table = Table()
    fields = ["name", "username", "dept", "email", "currency"]
    for header in fields:
        table.add_column(header, style="cyan")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    Console().print(table)


@main.command()
def create_user(
    name: str,
    email: str,
    dept: str,
    password: str,
    username: str | None = None,
    currency: str = "USD",
) -> User:
    """Creates a new user"""
    with Session(engine) as session:
        user = User(
            name=name,
            email=email,
            dept=dept,
            currency=currency,
            username=username or generate_username(name),
            password=password,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"User {name} created with id {user.id}")
        return user
