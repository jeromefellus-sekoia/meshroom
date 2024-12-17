import './TopPanel.scss'

export const TopPanel = {
    setup(props, { slots }) {
        return () => <div class='top-panel'>
            {slots?.default?.()}
        </div>
    }
}