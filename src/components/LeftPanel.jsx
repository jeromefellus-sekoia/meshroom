import './LeftPanel.scss'

export const LeftPanel = {
    setup(props, { slots }) {
        return () => <div class='left-panel'>
            {slots?.default?.()}
        </div>
    }
}