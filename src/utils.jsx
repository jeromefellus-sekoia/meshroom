import { onUnmounted } from "vue"
import { ERR } from './components/Toasts'

// OBJECT PROCESSING

/** Filter-out null fields from an object */
export const noNulls = (o) => Object.fromEntries(Object.entries(o).filter(([_k, v]) => ![null, undefined, ""].includes(v)))


// FORMATTING

/** Format date as a pretty string */
export const D = (x, br = false) => {
    if (typeof (x) === "string") x = new Date(x)
    if (typeof (x) === "number") x = new Date(x)
    x = x?.toLocaleString("fr-FR")
    if (br) return x?.split(" ").map(x => <div>{x}</div>)
    return x
}

/** Short-format for numbers */
export const NB = x => {
    if (x < 1000) return x
    x /= 1000.0
    if (x < 1000) return `${Math.round(x * 10) / 10}k`
    x /= 1000.0
    if (x < 1000) return `${Math.round(x * 10) / 10}M`
    x /= 1000.0
    return `${Math.round(x * 10) / 10}G`
}

/** Pretty format a time interval */
export const DELTATIME = (d, suffix) => {
    if (isNaN(d)) return "-"
    if (suffix) return `${DELTATIME(d)} ${suffix}`
    if (d < 1000) return `${d.toFixed(0)}ms`
    d = Math.round(d / 1000)
    if (d / 3600 / 24 === 1) return "1 day"
    if (d / 3600 === 1) return "1h"
    if (d / 60 === 1) return "1min"
    if (Math.round(d / 3600 / 24) === d / 3600 / 24) return `${(d / 3600 / 24).toFixed(0)} days`
    if (Math.round(d / 3600) === d / 3600) return `${(d / 3600).toFixed(0)}h`
    if (Math.round(d / 60) === d / 60) return `${(d / 60).toFixed(0)}min`
    if (d < 60) {
        if (d.toFixed(1).endsWith("0")) return `${d.toFixed(0)}s`
        return `${d.toFixed(1)}s`
    }
    d = d / 60
    if (d < 60) {
        const s = Math.floor((d - Math.floor(d)) * 60)
        if (s == 0) return `${d.toFixed(0)}min`
        return `${d.toFixed(0)}min ${s.toFixed(0)}s`
    }
    d = d / 60
    if (d < 48) {
        const m = Math.floor((d - Math.floor(d)) * 60)
        if (m == 0) return `${d.toFixed(0)}h`
        return `${d.toFixed(0)}h ${m.toFixed(0)}min`
    }
    d = d / 24
    if (d <= 1) return `1 day`
    return `${d.toFixed(0)} days`
}


// UTILITY FUNCTIONS

/** Debounce the given function */
export function debounce(f, timeout = 500) {
    let to = null;
    return (...args) => {
        if (to) clearTimeout(to);
        to = setTimeout(() => {
            f(...args)
            to = null;
        }, timeout)
    }
}


/** Repeat the given {cb} function every {interval} milliseconds, until the current Vue component vanishes */
export function repeat(cb, interval) {
    let i = null
    async function f() {
        await cb()
        if (i !== false) i = setTimeout(f, interval)
    }
    onUnmounted(() => { if (i) clearTimeout(i); i = false; })
    setImmediate(f)
}


// NETWORK

/** Submit a GET HTTP request */
export const GET = (url, params = {}) => fetch(url + "?" + new URLSearchParams(noNulls(params))).then(async x => {
    if (x.status >= 400) return await handleError(x)
    return x.json()
})

/** Submit a POST HTTP request */
export const POST = (url, params = {}) => fetch(url, {
    method: "POST",
    headers: new Headers({
        "content-type": "application/json"
    }),
    body: JSON.stringify(params)
}).then(async x => {
    if (x.status >= 400) return await handleError(x)
    return x.json()
})

/** Submit a PUT HTTP request */
export const PUT = (url, params = {}) => fetch(url, {
    method: "PUT",
    headers: new Headers({
        "content-type": "application/json"
    }),
    body: JSON.stringify(params)
}).then(async x => {
    if (x.status >= 400) return await handleError(x)
    return x.json()
})

/** Submit a DELETE HTTP request */
export const DELETE = (url, params = {}) => fetch(url, {
    method: "DELETE",
    headers: new Headers({
        "content-type": "application/json"
    }),
    body: JSON.stringify(params)
}).then(async x => {
    if (x.status >= 400) return await handleError(x)
    return x.json()
})


// ERROR HANDLING

/** Global error handling for all views */
async function handleError(x) {
    if (x.statusCode == 401) location.reload()
    let res = await x.text()
    ERR(res)
    try {
        res = JSON.parse(res)
        if (res.detail) throw res.detail
    } catch { }
    throw res
}


// PARSING

export const isIPV4 = x => {
    x = x.split(".")
    return x.length === 4 && !x.map(y => y.length > 0 && Number(y) >= 0 && Number(y) <= 255).includes(false)
}
export const isIPV4Range = x => {
    const [ip, l] = x.split("/")
    return Number(l) >= 0 && Number(l) <= 32 && isIPV4(ip)
}
export const isIPV6 = x => /^[\da-f:]+$/i.test(x) && !x.split(":").map(y => y.length <= 4).includes(false) && (x.split(":").length === 8 || (x.includes("::") && x.split("::").length <= 7))
export const isIPV6Range = x => {
    const [ip, l] = x.split("/")
    return Number(l) >= 0 && Number(l) <= 64 && isIPV6(ip)
}
export const isDomain = x => /^([A-Za-z][A-Za-z0-9\-\.]+)\.([A-Za-z][A-Za-z0-9\-\.]*[A-Za-z])$/.test(x)
export const isEmail = x => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(x)


export function one_at_a_time(fn) {
    let called = false
    return async (...args) => {
        if (called) return;
        called = true
        await fn(...args)
        called = false
    }
}