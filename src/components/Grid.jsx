import './Grid.scss'

export const Grid = (props, { slots }) => <div class='grid' {...props}>{slots?.default?.()}</div>