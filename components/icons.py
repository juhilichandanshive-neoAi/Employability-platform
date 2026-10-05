"""
Small inline icon set, hand-drawn to match the design pack's rule: one
family, outlined, rounded ends, nothing mixed in from anywhere else.
Streamlit can't put real icons inside a clickable st.button label, so these
render as SVG markup next to a plain-text button - see navigation.py.
"""

_ATTRS = 'width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'

ICONS = {
    "dashboard": f'<svg {_ATTRS}><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9a1 1 0 0 0 1 1H10v-6h4v6h3.5a1 1 0 0 0 1-1v-9"/></svg>',
    "profile": f'<svg {_ATTRS}><circle cx="12" cy="8" r="3.3"/><path d="M5 20c1-3.8 4-5.8 7-5.8s6 2 7 5.8"/></svg>',
    "assessment": f'<svg {_ATTRS}><rect x="5.5" y="4" width="13" height="17" rx="2"/><path d="M9 3.5h6a1 1 0 0 1 1 1V6H8V4.5a1 1 0 0 1 1-1Z"/><path d="m9 13 2 2 4-4.5"/></svg>',
    "score": f'<svg {_ATTRS}><path d="M4 15a8 8 0 0 1 16 0"/><path d="M12 15 15.5 10"/><circle cx="12" cy="15" r="1"/></svg>',
    "skill_gap": f'<svg {_ATTRS}><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4.2"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/></svg>',
    "roadmap": f'<svg {_ATTRS}><path d="M4 19 9 5l4 10 3-6 4 10"/><circle cx="9" cy="5" r="1.1" fill="currentColor" stroke="none"/><circle cx="16" cy="9" r="1.1" fill="currentColor" stroke="none"/></svg>',
    "certifications": f'<svg {_ATTRS}><circle cx="12" cy="9" r="5"/><path d="m8.5 13-1.5 7 5-2.5 5 2.5-1.5-7"/></svg>',
    "careers": f'<svg {_ATTRS}><rect x="3.5" y="8" width="17" height="11" rx="2"/><path d="M8.5 8V6a1.5 1.5 0 0 1 1.5-1.5h4A1.5 1.5 0 0 1 15.5 6v2"/><path d="M3.5 13h17"/></svg>',
    "jobs": f'<svg {_ATTRS}><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><path d="M2 13h20"/></svg>',
    "briefcase": f'<svg {_ATTRS}><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><path d="M2 13h20"/></svg>',
    "analytics": f'<svg {_ATTRS}><path d="M4 20V10M11 20V4M18 20v-7"/></svg>',
    "activity": f'<svg {_ATTRS}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "reports": f'<svg {_ATTRS}><path d="M7 3.5h7l4 4V19a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z"/><path d="M14 3.5V8h4"/><path d="M9 12h6M9 15.5h6"/></svg>',
    "settings": f'<svg {_ATTRS}><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3.9a7 7 0 0 0-2-1.2L14.2 3H9.8l-.4 2.6a7 7 0 0 0-2 1.2l-2.3-.9-2 3.4 2 1.5A7 7 0 0 0 5 12a7 7 0 0 0 .1 1.2l-2 1.6 2 3.4 2.3-1a7 7 0 0 0 2 1.2l.4 2.6h4.4l.4-2.6a7 7 0 0 0 2-1.2l2.3 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2Z"/></svg>',
    "search": f'<svg {_ATTRS}><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.3-4.3"/></svg>',
    "bell": f'<svg {_ATTRS}><path d="M6 17h12l-1.4-2A6.5 6.5 0 0 1 15.5 11V9.5a3.5 3.5 0 0 0-7 0V11a6.5 6.5 0 0 1-1.1 4Z"/><path d="M10.3 20a1.8 1.8 0 0 0 3.4 0"/></svg>',
    "logout": f'<svg {_ATTRS}><path d="M9 5H6.5A1.5 1.5 0 0 0 5 6.5v11A1.5 1.5 0 0 0 6.5 19H9"/><path d="M14 16l4-4-4-4"/><path d="M18 12H9"/></svg>',
    "book": f'<svg {_ATTRS}><path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5Z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5Z"/></svg>',
    "folder": f'<svg {_ATTRS}><path d="M4 6.5A1.5 1.5 0 0 1 5.5 5h4l2 2.5h8A1.5 1.5 0 0 1 21 9v8.5A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5v-11A1.5 1.5 0 0 1 4 6.5Z"/></svg>',
    "trend": f'<svg {_ATTRS}><path d="m3 16 6-6 4 4 8-9"/><path d="M15 5h6v6"/></svg>',
    "check-circle": f'<svg {_ATTRS}><circle cx="12" cy="12" r="8.5"/><path d="m8.5 12.5 2.3 2.3 4.7-5.1"/></svg>',
    "alert": f'<svg {_ATTRS}><path d="M12 4 3 19h18Z"/><path d="M12 10v4"/><circle cx="12" cy="16.5" r="0.6" fill="currentColor" stroke="none"/></svg>',
    "grid": f'<svg {_ATTRS}><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>',
    "link": f'<svg {_ATTRS}><path d="M10 14a4.5 4.5 0 0 0 6.4.3l2-2a4.5 4.5 0 0 0-6.4-6.4l-1.1 1.1"/><path d="M14 10a4.5 4.5 0 0 0-6.4-.3l-2 2a4.5 4.5 0 0 0 6.4 6.4l1.1-1.1"/></svg>',
    "zap": f'<svg {_ATTRS}><path d="M13 3 5 13h6l-1 8 8-11h-6Z"/></svg>',
    "star": f'<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"><path d="m12 3 2.6 5.9 6.4.6-4.8 4.3 1.4 6.3L12 17l-5.6 3.1 1.4-6.3-4.8-4.3 6.4-.6Z"/></svg>',
    "play": f'<svg {_ATTRS}><path d="M7 4.5v15l13-7.5Z"/></svg>',
    "download": f'<svg {_ATTRS}><path d="M12 3v12.5"/><path d="m7 11 5 5 5-5"/><path d="M5 19.5h14"/></svg>',
    "cloud": f'<svg {_ATTRS}><path d="M7 18h10.5a3.5 3.5 0 0 0 .5-6.96A5.5 5.5 0 0 0 7.6 9.1 4 4 0 0 0 7 18Z"/></svg>',
    "shield": f'<svg {_ATTRS}><path d="M12 3.5 5 6v6c0 4.5 3 7.5 7 8.5 4-1 7-4 7-8.5V6Z"/><path d="m9.5 12 1.8 1.8L15 10"/></svg>',
    "share": f'<svg {_ATTRS}><circle cx="18" cy="5" r="2.3"/><circle cx="6" cy="12" r="2.3"/><circle cx="18" cy="19" r="2.3"/><path d="m8.1 10.8 7.8-4.1M8.1 13.2l7.8 4.1"/></svg>',
}

ICONS["chevron-right"] = f'<svg {_ATTRS}><path d="m9 6 6 6-6 6"/></svg>'

BOTTOM_NAV_ICONS = {
    "dashboard": ICONS["dashboard"],
    "score": ICONS["score"],
    "skill_gap": ICONS["skill_gap"],
    "roadmap": ICONS["roadmap"],
    "profile": ICONS["profile"],
}


def icon(name: str, color: str = "currentColor", size: int = 20) -> str:
    svg = ICONS.get(name, "").replace("currentColor", color)
    if size != 20:
        svg = svg.replace('width="20" height="20"', f'width="{size}" height="{size}"')
    return svg
