import { ICON } from '../icons'
import './AppLogo.scss'

const APP_LOGOS = {
    user: ICON("people"),
    service: ICON("settings"),
    system: ICON("settings_suggest"),
    email: ICON("alternate_email"),
    unknown: ICON("help_center")
}

function infer_app_logo(app) {
    if (APP_LOGOS[app]) return APP_LOGOS[app]
    if (app.includes("openssh")) return APP_LOGOS['openssh']
    if (app.includes("apache")) return APP_LOGOS['apache']
    if (app.includes("windows")) return APP_LOGOS["windows"]
    if (app.includes("ubuntu")) return APP_LOGOS["ubuntu"]
    if (app.includes("linux")) return APP_LOGOS["linux"]
}


export const APP_LOGO = app => {
    if (!app) return;
    if (app.icon) return <span class="app-logo">
        <img src={app.icon} />
    </span>
    if (app.name) app = app.name
    else if (app.cve) app = app.cve
    else app = app.toString()
    app = app.replace(" ", "_")
    return <span class="app-logo" > {infer_app_logo(app?.toLowerCase()) || APP_LOGOS["unknown"]}</span>
}