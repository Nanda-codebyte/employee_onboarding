# Glassmorphism Visual Reference Guide

## 🎨 Color Palette

### Primary Colors
```
┌─────────────────────────────────────────┐
│ Primary Blue          #2563eb           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Used for: CTAs,  │
│                       accent text       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Primary Blue Light    #3b82f6           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Used for: hover   │
│                       states, lighter   │
│                       elements          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Primary Blue Dark     #1e40af           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Used for: active   │
│                       states, text      │
└─────────────────────────────────────────┘
```

### Secondary Colors
```
┌─────────────────────────────────────────┐
│ Teal                  #0d7377           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Gradient accent   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Teal Light            #14b8a6           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Lighter variant   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Green                 #06a77d           │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Success states    │
└─────────────────────────────────────────┘
```

### Neutral Colors
```
Text Colors:
┌─────────────────────────────────────────┐
│ Dark Gray #111827     ████████████     │ Primary text
│ Gray      #4b5563     ████████████     │ Secondary text
│ Light     #6b7280     ████████████     │ Muted text
│ Lighter   #9ca3af     ████████████     │ Disabled text
└─────────────────────────────────────────┘
```

### Glass Effect Colors
```
Background Layer:
  rgba(255, 255, 255, 0.12)
  ▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░ (12% opacity white)

Border Layer:
  rgba(255, 255, 255, 0.16)
  ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░ (16% opacity white)

Shadow Layer:
  rgba(8, 17, 32, 0.24)
  ▓▓▓▓▓▓░░░░░░░░░░░░░░░░ (24% opacity dark)
```

---

## 📐 Spacing System (Baseline: 4px)

```
xs:   4px    ░
sm:   8px    ░░
md:  16px    ░░░░
lg:  24px    ░░░░░░
xl:  32px    ░░░░░░░░
2xl: 48px    ░░░░░░░░░░░░

Visual Scale:
├─ xs ─┤
├──── sm ────┤
├────────── md ──────────┤
├───────────────── lg ──────────────┤
├──────────────────────── xl ──────────────────────┤
```

---

## 🎯 Border Radius Scale

```
sm:  8px     ┌──┐
             └──┘

md:  12px    ┌────┐
             └────┘

lg:  16px    ┌──────┐
             └──────┘

xl:  24px    ┌──────────┐
             └──────────┘
```

---

## 🔤 Typography System

### Font Families
```
Display: Outfit
┌─────────────────────────────┐
│ ABCDEFGHIJKLMNOPQRSTUVWXYZ │
│ abcdefghijklmnopqrstuvwxyz │
│ 0123456789                  │
└─────────────────────────────┘
Weights: 400, 500, 600, 700, 800

Body: Inter
┌─────────────────────────────┐
│ ABCDEFGHIJKLMNOPQRSTUVWXYZ │
│ abcdefghijklmnopqrstuvwxyz │
│ 0123456789                  │
└─────────────────────────────┘
Weights: 300, 400, 500, 600, 700
```

### Heading Scale
```
h1 │ Onboarding HQ                              │ 36px / 2.25rem │ Outfit 700
   │
h2 │ Dashboard                                  │ 30px / 1.875rem │ Outfit 700
   │
h3 │ Employee Progress                          │ 24px / 1.5rem  │ Outfit 700
   │
h4 │ Quick Actions                              │ 20px / 1.25rem │ Outfit 700
   │
h5 │ Secondary Heading                          │ 18px / 1.125rem │ Outfit 600
   │
h6 │ Minor Heading                              │ 16px / 1rem    │ Outfit 600
   │
p  │ Regular body text goes here with full     │ 14px / 0.875rem │ Inter 400
   │ line height for optimal readability        │                  │
```

---

## 💎 Glass Card Components

### Standard Glass Card (.glass-card)
```
┌────────────────────────────┐
│ ╭─ Glass Card (24px) ─╮    │
│ │                      │    │
│ │  Title              │    │
│ │  Content goes here  │    │
│ │                      │    │
│ ╰──────────────────────╯    │
│                             │
│ Background: rgba(255,255,255,0.12)
│ Border: 1px rgba(255,255,255,0.16)
│ Blur: 20px (primary)
│ Shadow: 0 18px 48px rgba(8,17,32,0.24)
│ Radius: 24px
└────────────────────────────┘
```

### Small Glass Card (.glass-card-sm)
```
┌──────────────────────┐
│ ╭─ Small Card ─╮     │
│ │  Content    │      │
│ ╰──────────────╯      │
│                       │
│ Blur: 12px (reduced)  │
│ Shadow: smaller       │
│ Radius: 16px          │
└──────────────────────┘
```

### Large Glass Card (.glass-card-lg)
```
┌───────────────────────────────────┐
│ ╭─ Large Card (32px padding) ─╮   │
│ │                              │   │
│ │  Headline                   │   │
│ │  Full content area          │   │
│ │  Multiple elements          │   │
│ │                              │   │
│ ╰──────────────────────────────╯   │
│                                     │
│ Blur: 24px (enhanced)               │
│ Shadow: 0 24px 64px (elevated)     │
│ Radius: 24px                        │
└───────────────────────────────────┘
```

---

## 📱 Sidebar Navigation Visual

```
┌──────────────────────────────┐
│  EMPLOYEE PORTAL             │
│  Onboarding HQ               │  ← Gradient text
│                              │
│  ┌─────────────────────────┐ │
│  │ 📊 Dashboard    Overview │ │  ← Active state
│  │    (Highlighted)        │ │
│  └─────────────────────────┘ │
│  │ ✅ Checklist    Tasks   │ │
│  │ 📋 Policies     Guidance │ │
│  │ 👥 HR Admin     Reports  │ │
│                              │
│  ─────────────────────────── │
│  Need help?                  │
│  Open HR Assistant           │  ← Link
└──────────────────────────────┘

Active Button Styling:
┌──────────────────────────────┐
│█ 📊 Dashboard    Overview    │  Background gradient
│  └─────────────────────────── ← Left accent bar
│
│  Transform: translateX(4px)
│  Icon scales: 1.15x
│  Font weight: 700 (bold)
└──────────────────────────────┘

Hover Button Styling:
┌──────────────────────────────┐
│  ░ ✅ Checklist    Tasks     │  Subtle background
│                             │  Transform: translateX(2px)
│                             │  Smooth transition
└──────────────────────────────┘
```

---

## 🔘 Button Styles

### Primary Button
```
┌────────────────────────────┐
│        Click Action        │  ← Gradient blue background
│                            │
│ Background: Linear gradient │
│ (135deg: #2563eb → #3b82f6)│
│ Color: White              │
│ Shadow: 0 8px 24px        │
│ Radius: 16px              │
│ Padding: 16px 24px        │
│                            │
│ On Hover:                  │
│  • Transform: translateY(-2px)
│  • Shadow: 0 12px 32px    │
└────────────────────────────┘
```

### Secondary Button
```
┌────────────────────────────┐
│        Cancel              │  ← Glass background
│                            │
│ Background: Glass effect   │
│ Border: Glass border       │
│ Color: Primary blue        │
│ Blur: 12px                │
│                            │
│ On Hover:                  │
│  • Background opacity ↑    │
│  • Transform: translateY(-2px)
└────────────────────────────┘
```

---

## 📝 Form Elements

### Input Field
```
┌────────────────────────────┐
│ ░ Enter text here...       │
│                            │
│ Background: Glass          │
│ Border: Glass border       │
│ Focus border: Primary blue │
│ Focus shadow: Blue glow    │
│ Radius: 12px              │
│ Padding: 12px 16px        │
└────────────────────────────┘

Focus State:
┌────────────────────────────┐
│ ░ Cursor is here│          │
│ Border: #2563eb            │
│ Box-shadow: 0 0 0 3px      │
│            rgba(37,99,235,.1)
│ Background lighter         │
└────────────────────────────┘
```

---

## ⚡ Animation & Transition Speeds

```
Fast:   150ms ease   ▁▂▃▄▅▆▇█
Base:   180ms ease   ▁▂▃▄▅▆▇█
Slow:   250ms ease   ▁▂▃▄▅▆▇█

Common animations:
• Hover state: base (180ms)
• Button press: fast (150ms)
• Page transition: slow (250ms)
```

---

## 📊 Layout Grid

### Desktop (≥1025px)
```
┌─────────────────────────────────────────────────┐
│ Sidebar   │           Main Content              │
│  280px    │           1fr                       │
│           │                                     │
│ Sticky    │  Glass cards with spacing           │
│ Position  │                                     │
└─────────────────────────────────────────────────┘
  24px gap between columns
```

### Tablet (768px - 1024px)
```
┌─────────────────────────────────────────────┐
│ Sidebar   │    Main Content                  │
│  240px    │    1fr                           │
│           │                                  │
│ Adjusted  │  Adjusted spacing                │
│ Spacing   │                                  │
└─────────────────────────────────────────────┘
  20px gap
```

### Mobile (<768px)
```
┌──────────────────────┐
│                      │
│   Main Content Only  │
│   (Full Width)       │
│                      │
│   Sidebar hidden     │
│   Single column      │
│                      │
└──────────────────────┘
  16px padding
```

---

## 🎬 Common Interaction Patterns

### Hover Animation
```
Normal:    ░░░░░░░░░░
           Position: 0

Hover:     ░░░░░░░░░░  ← translateY(-2px)
                    ↑
Transition: all 180ms ease
```

### Focus Animation
```
Before:    ┌──────────┐
           │  Input   │
           └──────────┘

Focus:     ┌──────────┐  ← Border color change
           │  Input   │  ← Shadow glow appears
           └──────────┘
                ↑ 3px box-shadow
```

### Active State Indicator
```
Inactive:  □ Menu Item
           
Active:    █ Menu Item  ← Left bar appears
           └─────────  ← Transform translateX
```

---

## 🎨 Gradient References

### Primary Gradient
```
Direction: 135°
─────────────→

Color 1: #0d3b66 (Dark teal)     █████░░░░░░░
Color 2: #1d7874 (Mid teal)      █████████░░░
Color 3: #06a77d (Light green)   ░░░░░░░███░
```

### Blue-to-Teal Gradient
```
Direction: 90°
───────────→

Color 1: rgba(56,189,248,0.35)   █████░░░░
Color 2: rgba(37,99,235,0.38)    ░░░░░█████
```

---

## 📐 Responsive Hierarchy

```
Desktop (1200px+):          h1: 36px, sidebar: 280px
┌─────────────────────────┐
│ 280px │ Main Content    │
├─────────────────────────┤

Tablet (768-1024px):        h1: 30px, sidebar: 240px
┌───────────────────────────┐
│ 240px │ Main Content      │
├───────────────────────────┤

Mobile (320-768px):         h1: 24px, sidebar: hidden
┌───────────────────┐
│  Main Content     │
├───────────────────┤

Small Mobile (<320px):      h1: 20px, padding: 8px
┌─────────────────┐
│  Main Content   │
├─────────────────┤
```

---

## ✨ Visual Depth Levels

```
Level 0 - Background
   Background gradient (135deg teal mix)
   
Level 1 - Base Glass Cards
   background: rgba(255,255,255,0.12)
   blur: 20px
   
Level 2 - Elevated Elements
   background: rgba(255,255,255,0.14)
   blur: 16px
   shadow: 0 8px 24px
   
Level 3 - Modal/Overlay
   background: rgba(255,255,255,0.16)
   blur: 24px
   shadow: 0 24px 64px
   
Level 4 - Interactive Feedback
   transform: translateY(-2px)
   enhanced shadow
```

---

**Visual Design System v1.0.0**  
*Glassmorphism Implementation for Employee Onboarding*  
*Created: July 12, 2026*
