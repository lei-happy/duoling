自检发现几处会真实出问题的冲突，先修：地图标记类名 `.pin` 与标注徽标 `.pin` 撞车、横幅内灰色文字在蓝底上不可读、画板进场动效在 JS 失败时会导致空白页。

I'm reviewing the HTML and CSS to catch any rendering issues, particularly with the color scheme. I notice the `.mut` span inside the banner might have a contrast problem—using dark gray text on a blue background would be hard to read, so I need to adjust that styling.

I'm also checking the cascade order for the `.pull-up` class to make sure the negative margin override works correctly, and I'm spotting an issue where inline margin styles on the notice element are blocking the pull-up effect entirely. The `.dev .map .pin` selector has higher specificity and overrides the map pin styling, but the global `.pin` properties that aren't explicitly redefined in the map context still cascade through—things like the size, border-radius, background color, and box-shadow all leak into the map pins unless I explicitly override them.

I need to rename the map pins to avoid this collision. `.mk` is already taken for photo watermarks, so I'll use `.mrk` instead. I'm updating the CSS selectors from `.dev .map .pin` to `.dev .map .mrk` and all related nested selectors, then updating the HTML to match.

Now I'm restructuring the tail element — instead of putting `::after` on the marker itself with `background:inherit` (which wouldn't work since the marker has no background), I'll attach it to the bubble. The bubble has an explicit background color via `var(--brand)`, so the tail's `::after` with `background:inherit` will correctly pick up that color. I need to make the bubble `position:relative` so the tail can be positioned absolutely below it.

Fixing the CSS and HTML now... Finishing up the map positioning — the SVG viewBox is 347x150 to fit the card width of 351 pixels, and I'm using `preserveAspectRatio="none"` to stretch it. The pin badge sits at the top-right of the card with `overflow:hidden` keeping it visible, and the marker bubble transforms to sit above its anchor point. Some unused utility classes aren't needed for this layout.

Now checking the timeline steps — there are 7 items across the width with labels like 派车, 接单, 装车 that are 2 characters each, fitting nicely into the 53-pixel space per step. The photo grid below uses a 6-column layout with square aspect ratios, giving roughly 50 pixels per image. The card styling applies a top margin override where needed, and the white background uses the card color variable for consistency.

I'm noticing the white background on screen 6 makes the cards blend in too much, so I should remove the white class and keep the page background gray instead. I'll also remove the flat styling from the first card to give it a shadow like the others for visual consistency.

Now I'm reviewing the component classes — the flag span for priority labels works well, the tag styling in steps is fine, and for the action bar buttons I have both a grow flex option and a wide option that achieve the same effect.

Looking at screen 1's action bar with the reject and receive buttons, the natural width button pairs nicely with the flex-grow button. But I'm noticing a potential clipping issue: the pin positioned at the top-left corner of the action bar will get cut off by the device's overflow hidden, since it extends outside the bounds.

I need to reposition the pin to sit inside the action bar instead. I could define a specific class like `.pin.on-bar` that places it at `top:-8px;left:14px` to keep it visible and properly contained, or I could adjust the existing `.tl` variant — though that's used elsewhere for cells so changing it globally might break other layouts. The inline style approach with `top:-8px;left:12px;right:auto` directly on the pin element would work cleanly for action bars specifically. I need to rethink the flex behavior for the key cell when it contains a sub-element — instead of using `:has()`, I'll make the key flexible with `flex:1 1 auto` and `min-width:0` so it can shrink, while the value cell uses `margin-left:auto` to stay right-aligned. Looking at the CSS specificity issue with `.lnk` and `.mut` classes — since `.lnk` is defined later in the stylesheet, it overrides the gray color from `.mut`, so I'm switching to use a `<span class="t3">` wrapper with an inline font-size instead to get the gray color I want.

Now checking the pagination styling with `.pg.g` and margin utilities, then moving on to the banner stat styling for the primary variant.

For the JavaScript, I'm verifying that the DOM queries work correctly — `querySelectorAll` with `forEach` on NodeLists is fine, and `closest('button')` for event delegation is solid. The status bar icons use the `.ico` class with fill and stroke variants, where the `.dev` scope applies the styling rules, and specific sizing is set via `.wx-status .sig .ico`.

The signal and wifi SVGs both have an 18-unit viewBox scaled down to 17px, which gives roughly a 1.6px stroke at the 1.7 stroke-width — the wifi arcs might look a bit thick, so I'm adjusting the wifi path stroke-width to 1.4 for better proportions. The time display uses monospace font via CSS custom property, which gives an authentic feel even though iOS actually uses SF Pro semibold. The font-weight is already set to 600 on the status container, so that's consistent.

Now I'm checking how the `.num` class cascades between the tabbar and device status sections — both define it with monospace font, and since `.dev .num` comes later in the stylesheet, its font-family wins, but the tabbar's font-size of 9.5px survives since the device version doesn't override it. The tabular-nums variant is only on the device version, which is fine for the time display.

Moving through the rest of the checklist: IntersectionObserver uses a Map to track seen elements, the rail builder toggles the 'on' class by coercing a truthy string to boolean (which works via the toggle method's force parameter), the reveal animation uses the index for stagger timing, and the board starts with opacity 0.

For the flash-of-unstyled-content issue, I'm considering whether to use a `<noscript>` fallback or a class-based approach. The safest pattern is to keep boards visible by default, then have the script add an `anim` class to the body at initialization before setting up observers, with CSS transitions that move boards from visible to hidden and back in. Since the script runs after the DOM parses, there will still be a brief flash, but it's unavoidable with this approach.

Actually, I'm reconsidering the whole reveal animation. The spec is static content, and a fade-in doesn't really serve a functional purpose — it's just decoration. The skill emphasizes restraint and removing unnecessary flourishes, so I should drop the reveal animation entirely and keep only the rail-hover highlight, which actually connects navigation to content and has real utility. This also eliminates the reduced-motion accessibility concern for the boards.

So I'm removing the reveal animation CSS rules and the `reveal()` function from the script, keeping just the highlight effect. Moving on to check other elements like `.pt-tools`.

Now I'm applying all the CSS and HTML fixes: adjusting the banner mutation color and opacity, renaming the map pin class and moving the tail styling, fixing cell flex properties, adding a dim link color variant, repositioning the action-bar pins, and updating the screen layouts for the map and notice sections.