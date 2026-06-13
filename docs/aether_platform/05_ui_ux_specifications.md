# AETHER Network: UI/UX System Specifications

This document outlines the screen architecture, component tree hierarchy, state management layout, and micro-interaction specifications for the **AETHER Network Command Center**.

---

## 1. Screen Architecture

The dashboard comprises five modular screens designed for high-density information displays.

1.  **Command Center (Overview)**: Real-time environmental metrics, Multi-Agent Control Tower status, alert lists, and primary city selectors.
2.  **Predictive Analytics Theater**: High-detail timelines showing historical trends (24h to 30d) and machine learning predictions with confidence intervals.
3.  **Simulation Arena (Digital Twin)**: A canvas render (Three.js) of the plant ventilation ducting and sensors, permitting interactive scenario testing.
4.  **Agent Control Tower**: Direct status audits of the agent network, displaying decision trees, confidence logs, and consensus details.
5.  **Compliance Ledger**: Interactive search index of historical logs with cryptographically-signed compliance records (CSV/PDF export).

---

## 2. Component Tree Hierarchy (Framer Motion specs)

```
[Main Application Layout]
 ├── [Header Hero Banner] (Dynamic greeting, city select, demo toggle, connection badge)
 ├── [Multi-Agent Executive Control Tower] (Row of Agent cards with glow indicators)
 ├── [Metrics Grid] (5 interactive glassmorphic metric cards)
 ├── [Main Analysis Dashboard] (Grid layout)
 │    ├── [Left: Analytics Panel]
 │    │    ├── [Chart: AQI Timeline]
 │    │    └── [Chart: PM2.5 Area Plot]
 │    └── [Right: Regional Heatmap & Pollution Composition]
 │         ├── [Chart: City AQI Bar Chart]
 │         └── [Chart: Pollution Composition Donut]
 └── [Bottom Audit Panels]
      ├── [Left: Historical Data Grid] (CSV download options)
      └── [Right: Autonomous Agent Audit Log] (Monospace scrolling logs stream)
```

---

## 3. Motion & Micro-Interaction Specifications

To create a fluid, premium desktop app feeling, AETHER uses spring-physics based animations at 60fps (implemented via Framer Motion):

### Card Hover Effect
*   **Trigger**: Cursor hover on `.metric-card` or `.agent-card`.
*   **Transition**:
    *   `scale`: `1.02` (spring: stiffness `300`, damping `20`)
    *   `box-shadow`: Increase glow radius using `drop-shadow` on cyan/purple accent vectors.
    *   `border-color`: Fade from `rgba(255,255,255,0.06)` to `var(--accent-cyan)` or `var(--accent-purple)`.

### Ambient Breathe Pulse
*   Active state indicators pulse continuously to signal live socket connection:
    *   `opacity`: Transition from `0.4` to `1.0` in a sinusoidal curve over 3 seconds.
    *   `box-shadow`: Pulsing blur radius from `4px` to `16px`.

---

## 4. Accessibility & Inclusive Design (WCAG 2.2 AAA)

*   **Color-Blind Safety**: High-contrast outline borders are added to warning elements so that colors are not the sole indicators of status breaches.
*   **Keyboard-First Navigation**: Full keyboard navigation across all dropdown inputs, sliders, and buttons using standard semantic DOM tagging and `tabindex`.
*   **Contrast Ratios**: All text elements maintain a minimum contrast ratio of **7:1** against the dark void background.
