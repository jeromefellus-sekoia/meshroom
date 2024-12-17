import './Severities.scss'

export const Severities = ({ scores }) => {
    const max = Math.max(...Object.values(scores))
    return <div class="severities">
        {["critical", "high", "medium", "low"].map(severity => <span title={severity} class={`sev-${severity}`} class={{ zero: !scores[severity] }}>
            {scores[severity] || 0}
            <span style={{ height: `${(scores[severity] || 0) * 100 / max}%` }} />
            <b>{scores[severity] || 0}</b>
        </span>)}
    </div>
}