# Overview

Creative North Star: The verified talent desk. The interface should feel like a calm recruiting workspace where a user can scan, filter and act without visual friction.

This is a product interface. Use predictable structure, restrained colour and consistent density. Marketing pages may be more expressive, but search, profile and account screens must prioritise clarity.

# Colors

Primary ink is deep CVLink navy, used for navigation, headings and important text. Orange is the committed accent and should be used for primary actions, active filters, selected states and small emphasis only. Surfaces are white and cool near-white. Neutral borders are cool slate.

Do not use gradients for text. Do not use orange as decoration on inactive elements. Avoid warm cream backgrounds.

# Typography

Use one product sans stack: Aptos, Segoe UI Variable, Segoe UI, system-ui and platform fallbacks.

Use a fixed product scale, not large fluid display type, on app screens. Search and profile screens should keep headings compact. Use 600 to 700 weight for headings and 500 to 650 for controls. Avoid very heavy 800 to 900 weights except for rare labels that need strong emphasis.

# Elevation

Flat by default. Use a 1px border for structure and a small shadow only when a surface must separate from the background. Never combine heavy shadows with heavy borders. Cards top out at 12px to 16px radius.

# Components

Buttons use one shape and clear state vocabulary. Primary buttons are orange. Secondary actions use navy or a neutral outline. Inputs are 44px to 48px tall with visible labels and strong focus states.

Talent result cards are list rows, not marketing cards. They should support fast scanning with photo, identity, status, skills and actions aligned to a predictable grid.

Filter panels are work controls. On desktop, keep filters in a stable rail. On mobile, make the filter entry obvious and do not hide the main search task below long controls.

# Do's and Don'ts

Do use spacing tokens based on 4, 8, 12, 16, 24, 32, 48 and 64px.

Do group related controls tightly and separate distinct regions clearly.

Do use orange for the primary action and selected filter states.

Do preserve visible focus states.

Don't use glassmorphism as a default surface.

Don't use oversized radii on cards or inputs.

Don't let legacy CSS layers compete with current layout rules.

Don't ship text with broken accents.
