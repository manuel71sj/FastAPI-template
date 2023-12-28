from pathlib import Path
from pprint import pprint

from cookiecutter.exceptions import (FailedHookException,
                                     OutputDirExistsException)
from cookiecutter.main import cookiecutter
from termcolor import cprint

from fastapi_template.cli import run_command
from fastapi_template.input_model import BuilderContext

script_dir = Path(__file__).parent


def generate_project(context: BuilderContext) -> None:
    """
    Generate actual project with given context.

    :param context: builder_context
    """
    try:
        aa = context.dict()
        bb = BuilderContext().dict()
        pprint(aa)
        pprint(bb)
        cookiecutter(
            template=f"{script_dir}/template",
            extra_context=aa,
            # default_config=bb,
            no_input=True,
            overwrite_if_exists=context.force,
        )
    except (FailedHookException, OutputDirExistsException) as exc:
        if isinstance(exc, OutputDirExistsException):
            cprint("Directory with such name already exists!", "red")
        return
    cprint(
        "Project successfully generated. You can read information about usage in README.md"
    )


def main() -> None:
    """Starting point."""
    run_command(generate_project)


if __name__ == "__main__":
    main()
