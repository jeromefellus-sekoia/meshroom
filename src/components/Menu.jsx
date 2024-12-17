import './Menu.scss'

export const Menu = {
    setup(props, { slots }) {
        return () => {

            return <nav class="menu">
                {slots?.default?.()}
            </nav>
        }
    },

    Item: ({ icon, to }, { slots }) => <router-link class="menu-item" to={to}>
        <div class="icon">{icon}</div>
        {slots?.default?.()}
    </router-link>
}
