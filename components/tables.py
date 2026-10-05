"""
One table pattern used everywhere: a real table on a wide screen, the same
rows as stacked cards on a phone. Both are rendered; styles.css shows only
one of them depending on viewport width, so nothing has to be recomputed
on resize.
"""

import streamlit as st
from components.html import flatten_html, render_html


def responsive_table(headers, rows, mobile_row_renderer):
    with st.container(key="table-desktop"):
        render_html(_table_html(headers, rows))
    with st.container(key="table-mobile"):
        for row in rows:
            render_html(flatten_html(mobile_row_renderer(row)))


def _table_html(headers, rows):
    thead = "".join(f"<th style='text-align:left;padding:8px 12px;font-size:12px;color:#6B6478;text-transform:uppercase;letter-spacing:.04em;'>{h}</th>" for h in headers)
    body_rows = ""
    for row in rows:
        cells = "".join(f"<td style='padding:10px 12px;border-top:1px solid #E5E1F0;font-size:14px;'>{c}</td>" for c in row)
        body_rows += f"<tr>{cells}</tr>"
    return f"""
    <div class="ea-card" style="padding:0;overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr>{thead}</tr></thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
    """
