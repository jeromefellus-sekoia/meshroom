import { ICON } from '../icons'
import { UI } from '../main'
import './Toasts.scss'

export const Toasts = {
    setup(props, { slots }) {
        return () => {
            return <div id="toasts">
                {UI.toasts?.map(t => <Toast class={t.cls} ref={x => {
                    if (x && !x?.classList.contains("show")) {
                        setImmediate(() => x?.classList.add("show"))
                        setTimeout(() => x?.classList.remove("show"), 2500000)
                    }
                }}>
                    {t.icon} {t.msg}
                </Toast>
                )}
            </div>
        }
    }
}

export const Toast = (props, { slots }) => <div class="ui-toast">{slots?.default?.()}</div>


export function TOAST(msg, icon = null, cls = null) {
    const id = +new Date()
    UI.toasts.push({ msg, id, icon, cls })
    while (UI.toasts?.length > 4) UI.toasts.shift()
    setTimeout(() => {
        UI.toasts = UI.toasts.filter(t => t.id !== id)
    }, 3000)
}

export function ERR(msg) {
    return TOAST(msg, ICON("error"), "error")
}