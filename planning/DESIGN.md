# The Saturation Point — Pen Care Studio

Design direction for a PySide6 desktop application · 2026-11-06 · Planning artifact

## Product and experience

Pen Care Studio is a staff-facing service desk for fountain-pen cleaning, ink flushing, nib inspection, and care requests. It extends The Saturation Point's pen, ink, and paper shop into aftercare. The primary job is to move a customer's pen from intake to pickup without losing its condition notes, estimate, due date, or history.

**Design promise:** a calm, precise workshop ledger. It should feel like a premium stationery counter, but behave like a fast service tool. The interface should earn its character through typography, material colors, careful alignment, useful detail, and small craft references—not decorative clutter or a generic grid of cards.

The first release is a single-window, staff-operated desktop app. It should work offline with a local database. It does not need a customer portal, live payments, maps, or a connection to the MERN store. Those are product-scope choices for this project, not limitations of PySide6.

## Staff tasks and information hierarchy

The UI should make these tasks obvious within one or two actions:

1. Find a job by ticket number, customer, pen, or status.
2. Register a pen and document its condition at intake.
3. Record the requested care services, estimate, and promised date.
4. Advance a job through its permitted status changes.
5. Check what is due today or overdue.
6. Mark a completed job as claimed and produce a clear receipt or service summary.

The information hierarchy is **job identity → status and due date → customer and pen → work details → price → history**. A user should not have to open a detail page to see whether a ticket is urgent.

## Navigation and screen structure

Use one `QMainWindow` with a persistent, narrow left navigation rail and a content area. Keep the main navigation to **Overview**, **Jobs**, **Customers**, **Services**, and **Reports**. A small Settings entry can sit at the bottom. Do not create navigation for every status; statuses belong in the Jobs view as filters.

The [Jobs screen visual reference](./pen-care-studio-reference.svg) shows the intended hierarchy at a desktop size: a quiet rail, compact operational counts, searchable work queue, and selected-job detail pane. It is a direction for visual review, not a pixel-perfect mandate. The new build should adapt it to real font metrics, window sizes, and native Qt behavior.

The rail gives orientation; the page title and main action establish priority. The summary line is operational, not a decorative dashboard. Use one primary action per screen. A selected job opens a detail view with a clear header, status, due date, intake notes, requested work, estimate, and chronological activity. On wide windows, a resizable list/detail split is useful; on narrower windows, open the detail as the main content and provide a visible Back to jobs action. Avoid stacking multiple modal dialogs.

The Overview should show **Due today**, **Overdue**, **Ready for pickup**, and **Recently updated**, each linking into a filtered Jobs list. It should be a triage page, not an analytics landing page. Reports can be modest: jobs by status, completed services, turnaround time, and revenue recorded from completed jobs.

## Visual language

Retain the MERN brand's charcoal, warm white, gold, Lora headings, and Montserrat body text. Shift from its storefront presentation to a quieter workshop surface: more room for tables and forms, fewer large hero elements.

| Token | Proposed value | Use |
|---|---|---|
| Canvas | `#FAF9F6` | Main application background |
| Surface | `#FFFFFF` / `#FFFDF8` | Tables, forms, detail panels |
| Ink | `#1C1917` | Main text and primary button fill |
| Secondary ink | `#44403C` | Supporting text |
| Muted ink | `#78716C` | Timestamps and tertiary labels on light surfaces |
| Brand gold | `#CA8A04` | Short rules, selection marks, small decorative accents |
| Accessible gold text | `#8C5A00` | Gold text or outline on cream/white |
| Hairline | `#E8E2D8` | Section and row dividers |
| Error | `#9F1239` | Errors and destructive actions, paired with text |
| Success | `#166534` | Completed/claimed status, paired with text |
| Informational | `#1E40AF` | Links or neutral progress messages |

The existing brand gold `#CA8A04` has only about **2.94:1 contrast on white** and **2.79:1 on the cream canvas**. Do not use it for normal-size text on those surfaces. `#8C5A00` is about **5.87:1 on white** and **5.58:1 on cream**; use that darker gold for readable text. Calculations use the WCAG relative-luminance formula, and all final color pairings still need visual and automated checking. Aim for at least **4.5:1 for ordinary text** and **3:1 for large text** per [WCAG contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum). Do not communicate job status using color alone.

Use Lora only for the application wordmark, page titles, and occasional section headings. Use Montserrat for labels, forms, table cells, buttons, and body copy. Fall back to a readable system font if bundled fonts fail. Suggested starting sizes: body 10–11 pt, table 10 pt, secondary 9–10 pt, page title 22–26 pt. Prefer comfortable line height and visible weight changes to excessive font-size jumps. Bundle licensed font files locally rather than depending on network access.

Use an 8-unit spacing rhythm: 8 for tightly related controls, 16 for fields and row groups, 24 for panel padding, 32 for major section breaks. These are starting values to tune with native font metrics. Keep border radii subtle (roughly 6–8 logical px); the original store's square-edge character can remain in dividers and button geometry. Use shadow sparingly. A fine gold rule or nib silhouette is enough to carry the brand.

Use a small, coherent icon set with line weight and optical size aligned. Icons support labels; they do not replace them for primary actions. Avoid stock photography, gradients behind data, floating cards for every statistic, ornamental script fonts, and large empty dashboard regions.

## Avoiding generic AI-generated design

“AI slop” is a critique of the result, not a reliable way to determine how a screen was made. The useful test is whether the interface reflects this service desk's real tasks and brand. Nielsen Norman Group found that underspecified AI prototypes often converge on flat, interchangeable styling, inappropriate page templates, repeated information, and prominent containers with little useful content ([AI prototyping in real contexts](https://www.nngroup.com/articles/ai-prototyping/), [prompt-to-design study](https://www.nngroup.com/articles/vague-prototyping/)). The checks below turn those observations into design-review criteria for this app. Some visual examples are our project-specific judgments rather than universal anti-patterns.

| Warning sign in a draft | Why it is weak here | Replace with |
|---|---|---|
| A row of four giant number cards before the job queue | Staff must scroll past statistics before finding due work | A compact operational summary above the queue; make each count open the corresponding filtered list |
| Every section in an identical rounded white card with shadow | It erases hierarchy and resembles a generic web dashboard | One main work surface, fine dividers, and selective panels only where a boundary helps |
| A gradient hero, abstract blobs, glowing buttons, or generic pen stock art | They add decoration without helping intake or triage | A restrained wordmark, a fine gold rule, and precise pen/ink terminology |
| Repeated status counts, progress rings, and charts showing the same fact | Redundancy occupies useful workspace | Show each metric once, near the action it informs |
| Placeholder content such as “John Doe,” “Service A,” or implausible totals | It hides whether the layout works with real names and cases | Test with realistic pen models, long customer names, missing dates, overdue jobs, and zero-result searches |
| A customer-profile banner dominating the Jobs screen | It focuses on a secondary entity instead of the repair queue | Lead with ticket, due date, status, and pen; show customer details in the job view |
| Too many pill filters, emoji icons, and hover-only controls | They look templated and weaken desktop scanability/keyboard use | A small set of labeled filters, consistent line icons, visible focus, and text actions |
| Arbitrary gold text, pale gray labels, or color-only status | “Premium” styling reduces legibility | Use the tested color tokens and pair color with explicit status text |
| Generic marketing copy such as “Streamline your workflow” inside the app | It does not help a staff member act | Direct operational language: “4 jobs due today” or “Add condition notes before saving” |
| A dense table wrapped in a fake browser-style dashboard shell | PySide6 is a desktop tool with native interaction conventions | Use the Qt main-window frame, real table selection, keyboard shortcuts, and a resizable detail pane |

The goal is **specificity rather than novelty for its own sake**. A simple table is right for a job queue if its columns, sorting, density, and actions match the work. Conversely, a beautiful mockup still fails if intake takes too many steps or the next status is unclear. NN/G's research also warns that visual fidelity alone does not guarantee coherent hierarchy or task flow ([prompt-to-design study](https://www.nngroup.com/articles/vague-prototyping/)). Apple’s broader design guidance makes the same useful distinction between delight and decoration ([design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles/)).

For every generated screen, review it against **three concrete scenarios** before accepting it: (1) a new Lamy Safari arrives for cleaning with condition notes and a due date; (2) a staff member must find an overdue Pilot Custom ticket in seconds; (3) a customer arrives to collect a ready pen and needs a clear service summary. If the layout does not make these scenarios easier, remove the decorative element or change the hierarchy. Preserve screenshots of each iteration and note what was kept or rejected. The `DESIGN.md` should remain a living input to the build rather than a one-time prompt; curated context is specifically recommended to reduce average, generic AI output ([NN/G on UX context and DESIGN.md](https://www.nngroup.com/articles/ux-context-design/)).

## Component behavior

**Primary button:** dark ink fill, light text, clear active/hover/focus/disabled states. Use for New intake or Save. **Secondary button:** quiet outline or text treatment for Cancel, Edit, and Back. **Destructive button:** separate from Save and require a clear confirmation when irreversible. Place related actions together; avoid placing Edit and Delete at opposite ends of a wide header.

**Job table:** show ticket, customer, pen model, service, due date, status, and optionally estimate. Default to urgent/due-soon ordering or most recently updated according to the task; state the current sort visibly. Use full-row selection, generous row height, a visible selected state, and a detail panel or double-click/open action. Preserve the user's search and filters on return. Long names should elide with a tooltip or be readable in details, not make columns jitter. Numeric prices and dates should sort by typed values, not formatted strings.

**Status chips:** always include words (Received, Inspecting, In service, Ready, Claimed, Cancelled). Use subdued tinted backgrounds and dark text. Reserve alarming red for overdue or error; ordinary work in progress should not look like failure. Show the next allowed transition prominently and put uncommon transitions in a menu.

**Forms:** intake is one focused task, divided into Customer, Pen, Condition, Service, and Handover. Use persistent labels, example text only when helpful, and appropriate widgets (`QDateEdit`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QTextEdit`). Mark optional fields explicitly. Show calculated totals beside their components. Keep a short condition checklist plus free notes; it reduces ambiguity at pickup. On errors, retain all entered data, show the issue near the field, and move focus to the first problem. For a long form, add a brief error summary at the top. This follows the principle of field-level feedback plus a summary in [GOV.UK's error guidance](https://design-system.service.gov.uk/components/error-summary/).

**Empty, loading, and failure states:** distinguish “no jobs yet,” “no search matches,” and “could not load jobs.” Give each one a next action. A blank table is not an adequate state. Save operations should disable duplicate submission, show progress if perceptible, and end with a specific confirmation such as “Ticket PC-0421 saved.” If printing fails, the job must remain saved and the user should be able to retry printing.

## Key flows

### New intake

Start with one clear New intake action. Enter or select customer; record pen brand/model and visible condition; choose service(s); enter estimate and due date; review a compact summary; save. After saving, show the ticket number and offer Print intake slip or View job. Do not ask for payment details merely to create a care job.

### Work queue

The staff member searches or filters by status and due date, opens a ticket, reviews prior notes, adds a work note, and advances to the next status. The activity timeline records who changed what and when. A status change should be confirmed inline with an undo opportunity where practical; irreversible cancellation requires an explicit confirmation with the ticket number.

### Pickup

For Ready jobs, show the final service summary, amount due/paid status, pickup date, and a Mark claimed action. Use clear human language in the receipt; do not expose internal enum names or database IDs except the ticket reference.

## PySide6 implementation guidance

Use `QMainWindow` as the shell, with a central `QStackedWidget` or equivalent page container, a persistent navigation rail, a top action/search area, and a small `QStatusBar`. Qt documents `QMainWindow` as the framework for menus, toolbars, docks, and status bars; use those features deliberately rather than building a web-page imitation inside one widget ([Qt main window](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMainWindow.html)).

Use `QTableView` with a model and `QSortFilterProxyModel` for the job queue so sorting, filtering, and selection remain separate from the underlying records. `QStyledItemDelegate` can render subtle status chips while keeping native selection and focus behavior. Use `QFormLayout` for short label/field groups and layout managers for all resizing. Avoid manually positioned widgets. These are supported patterns in [Qt's model/view guide](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-model-view-programming.html), [sort/filter model](https://doc.qt.io/qtforpython-6.10/PySide6/QtCore/QSortFilterProxyModel.html), and [form layout](https://doc.qt.io/qtforpython-6.11/PySide6/QtWidgets/QFormLayout.html).

Start with a native or Fusion style and a carefully adjusted `QPalette`. Use localized style-sheet rules only where a palette and native style cannot express a small brand detail. Avoid a giant application-wide QSS theme: Qt notes that broad style sheets can replace native drawing, require all widget states to be specified, and become costly to repolish ([Qt styling approaches](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-styling-approaches.html), [QPalette](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html)). This is an implementation choice for a polished, maintainable Widgets app, not a ban on QSS.

Package icons and fonts with Qt resources (`.qrc`, compiled with `pyside6-rcc`) so the interface works offline and after packaging ([Qt resource compiler](https://doc.qt.io/qtforpython-6.11/tools/pyside-rcc.html)). Store window size and optional splitter position via `QSettings`, but restore only application-owned state. Use Qt layouts and test at Windows 100%, 125%, 150%, and 200% display scaling; Qt's high-DPI handling uses logical coordinates and device-pixel ratios ([Qt high-DPI overview](https://doc.qt.io/qtforpython-6/overviews/qtdoc-highdpi.html)). Keep slow database, image, or printing work from blocking the event loop; use a worker where needed and return results to the GUI thread.

## Accessibility and input

All primary tasks must work by keyboard. Provide visible focus, sensible Tab order, Enter/Space activation, Escape for dismissing dialogs, and a few discoverable shortcuts (for example Ctrl+N for intake and Ctrl+F for search). Give icon-only buttons an accessible name with `setAccessibleName`; Qt notes that icons alone need this for screen readers ([QWidget accessibility](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html)).

Aim for comfortably sized click targets, especially in table action areas, and leave enough spacing between adjacent destructive and safe actions. WCAG's web benchmark is **24 × 24 CSS px or sufficient spacing**; use it as a practical floor for desktop interaction, then test at display scaling ([W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)). Never rely on color alone, disabled state alone, or a tooltip alone to explain what to do.

## Review gates for the new build

- At 1280 × 800 and 1024 × 700, the main tasks fit without clipped actions or horizontal window scrolling; long tables may scroll internally.
- At Windows 125%, 150%, and 200% scaling, text and icons remain crisp and all forms remain usable.
- Search, filter, selection, sorting, and status changes preserve context and behave predictably.
- Intake and status forms show field-specific errors, retain input, and prevent duplicate saves.
- Empty, loading, failure, success, and overdue states are visually distinct and worded clearly.
- Body text meets the contrast target; gold accents are not used as low-contrast body text.
- Keyboard-only navigation reaches every action, and icon-only controls have accessible names.
- Screenshots of Overview, Jobs, Job detail, New intake, and receipt preview are reviewed side by side for spacing, typography, and brand consistency.
- Each screen passes the three real-task scenarios in “Avoiding generic AI-generated design”; reject duplicated metrics, decorative hero panels, and low-information cards unless they solve a documented task.

This document is a design brief for the separate PySide6 implementation conversation. It should guide decisions and be revised after the first real-screen review; it is not a demand to build every optional feature in the first iteration.


## Readability refinement — November 2026

- Use 11 pt Segoe UI for body and tables, 24 pt Georgia page headings, and 42 px minimum primary control height. Table fonts are explicit because Qt item views can otherwise retain the smaller platform default under stylesheets.
- Keep due dates and worded status badges visible by grouping pen and customer into a two-line queue column. Services remain searchable and appear in selected-job details.
- Overview pairs actionable triage rows with recent tickets. Services use a numbered care menu with aligned prices and short descriptions. Reports separate recorded payments from claimed estimates in a ledger layout.
- On narrow windows, selection opens a full-width workbench with Back to queue. Short screens use scrolling content rather than smaller text; dialog actions stay outside scrolling forms.
- Preserve the existing SQLite schema and operations. The redesign changes presentation, not stored values, service prices or allowed transitions.

Reference: Microsoft Windows [typography](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography) and [spacing](https://learn.microsoft.com/en-us/windows/apps/design/style/spacing) guidance informed the stronger type hierarchy and grouping.
