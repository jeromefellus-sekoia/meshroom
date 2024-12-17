import './BottomPanel.scss'

export const BottomPanel = {
    setup(props, { slots }) {
        return () => <div class='bottom-panel'>
            {slots?.default?.()}
        </div>
    }
}