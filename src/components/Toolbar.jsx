import './Toolbar.scss'

export const Toolbar = (props, { slots }) => <div class='toolbar'>{slots?.default?.()}</div>