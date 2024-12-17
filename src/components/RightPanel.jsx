import { ICON } from "../icons"
import { UI } from "../main"
import "./RightPanel.scss"
import { ToolButton } from "./ToolButton"

let el = null


// Close right panel via click somewhere else or hit ESCAPE key
window.addEventListener("click", () => {
    if (UI.rightPanel && el?.classList?.contains("open") && !el?.is_opening) closeRightPanel()
})
window.addEventListener("keydown", e => {
    if (e.key === "Escape") {
        if (UI.rightPanel && el?.classList?.contains("open")) closeRightPanel()
    }
})


export const RightPanel = {
    setup(props, { slots }) {


        return () => {

            function open(e) {
                if (!e) return;
                el = e
                el.is_opening = true
                setImmediate(() => el.classList.add("open"))
            }

            return <div id="right" ref={open} onClick={e => { e.stopPropagation(); e.preventDefault(); }}>
                <ToolButton class="btn-close" onClick={closeRightPanel}>{ICON("close")}</ToolButton>
                {slots?.default?.()}
            </div>
        }
    }
}

export function closeRightPanel() {
    setImmediate(() => el.classList.remove("open"))
    setTimeout(() => UI.rightPanel = null, 400)
}