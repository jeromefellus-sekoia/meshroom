import { reactive } from 'vue';
import './ContextMenu.scss'

export function contextMenu(anchorEl, node, klass) {
    if (anchorEl.target) {
        anchorEl.stopPropagation();
        anchorEl.preventDefault();
        anchorEl = anchorEl.target
    }

    CONTEXT_MENU.contextMenu = {
        node,
        anchorBounds: anchorEl.getBoundingClientRect(),
        anchorEl,
        klass
    }
}

export const ContextMenu = {
    setup(props) {
        return () => {
            let { anchorBounds: { x, y, height, width }, node, klass } = CONTEXT_MENU.contextMenu
            if (typeof (node) === "function") node = node()
            const left = x > window.innerWidth * 0.7 ? null : (x) + "px";
            const right = !left ? (window.innerWidth - x - width) + "px" : null;
            const top = (y + height + 2) + "px";
            return <div class="context-menu" class={klass} style={{ left, right, top, "min-width": `${width}px` }} onClick={e => { CONTEXT_MENU.contextMenu = null; e.stopPropagation(); e.preventDefault() }}>
                {node}
            </div>
        }
    }
}


export const CONTEXT_MENU = reactive({
    contextMenu: null,
})

window.addEventListener("click", () => {
    CONTEXT_MENU.contextMenu = null;
})
