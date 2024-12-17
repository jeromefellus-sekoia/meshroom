import "./ProgressBar.scss"

export const ProgressBar = ({ value = 0 }) => <div class="progress">
    <div class="progress-bar" role="progressbar" style={{ width: `${value * 100}%` }} aria-valuenow={value * 100} aria-valuemin="0" aria-valuemax="100">
        <span>{(value * 100)?.toFixed(0)}%</span>
    </div>
</div>