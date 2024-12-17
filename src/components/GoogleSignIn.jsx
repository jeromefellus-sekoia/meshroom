import './GoogleSignIn.scss'
import { UI } from '../main'
import { ICON, Icon } from '../icons'

export const GoogleSignIn = ({ clientId, login, logout }) => {
    window.__google_onSignIn = login
    return <div class="avatar" class={{ authenticated: UI.authenticated }}>{UI.authenticated ? <div>
        <span class="avatar-icon">{UI.picture ? <img src={UI.picture} /> : ICON("face_3")}</span>
        <div class="name">{UI.username}<br /><i>{UI.email}</i></div>
        <button onClick={logout} title='logout'><Icon>logout</Icon></button>
    </div> : (clientId && <>
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <div id="g_id_onload"
            data-client_id={clientId}
            data-callback="__google_onSignIn"
            data-auto_prompt="false"
            data-ux_mode="popup"
        >
        </div>
        <div class="g_id_signin"
            data-type="standard"
            data-size="large"
            data-theme="outline"
            data-text="sign_in_with"
            data-shape="rectangular"
            data-logo_alignment="left">
        </div>
    </>)}
    </div>
}