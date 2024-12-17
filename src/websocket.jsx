import { onBeforeUnmount } from "vue"
import { one_at_a_time } from "./utils"

/** Subscribe to a websocket channel */
export function websocket_subscribe(channel, callback, { oneAtATime = true } = {}) {
    if (oneAtATime) callback = one_at_a_time(callback)
    const sub = new Subscription(channel, callback)

    // Automatically unsubscribe when the wrapping Vue component unmounts, if any
    try { onBeforeUnmount(() => sub.close()) } catch { }

    return sub
}


// Private

let ws = null

function connect() {
    ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/websocket`)
    ws.onclose = () => setTimeout(connect, 1000)
    ws.onmessage = e => {
        let data = e.data
        try { data = JSON.parse(e.data) } catch { }
        const { labels, ...rest } = data
        Subscription.all?.forEach(s => {
            if (labels?.includes(s.label)) {
                s.callback?.(rest)
            }
        })
    }
}
connect()

class Subscription {

    static all = []

    constructor(channel, callback) {
        this.channel = channel
        this.callback = callback
        Subscription.all.push(this)

        const subscribe = () => {
            if (ws?.readyState === WebSocket.CONNECTING) {
                setTimeout(subscribe, 500)
            } else if (ws?.readyState === WebSocket.OPEN) {
                this.send({ "subscribe": channel })
            }
        }
        subscribe()
    }

    close() {
        const i = Subscription.all.indexOf(this)
        if (i >= 0) Subscription.all.splice(i, 1)
        try {
            this.send({ "unsubscribe": this.channel })
        } catch { }
    }

    send(data) {
        ws?.send(JSON.stringify(data))
    }
}
