import "./Flag.scss"
export const Flag = ({ code = "fr" }) => <span title={code} class={`flag-icon flag-icon-${code}`} />