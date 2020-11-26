from enum import Enum

from flask import flash, redirect, render_template


class FlashCategories(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class FlashMessage:
    def show_with_render_template(self, message: str, category: FlashCategories,
                                  template_file: str, **context_dict: dict):
        flash(message, category.value)
        return render_template(template_file, **context_dict)

    def show_with_redirect(self, message: str, category: FlashCategories, url: str):
        flash(message, category.value)
        return redirect(url)
