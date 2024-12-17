import './Card.scss'

export const Card = ({ top, large, cols, header, title, n, subtitle, icon, iconColor, height, noborder, nopadding, ...rest }, { slots }) => <div class='card' {...rest} class={{ large, noborder, nopadding, top }} style={cols && { gridColumn: `span ${cols}` }} style={{ height }}>
    {(header || title) && <header>
        {icon && <div class="icon" style={{ background: iconColor }}>{icon}</div>}
        <div class="title">
            {title && <h3><span>{title}</span> {!isNaN(n) && <div class="flex right kpi">{n}</div>}</h3>}
            {subtitle && <h4>{subtitle}</h4>}
            {header}

        </div>
    </header>}
    <div>
        {slots?.default?.()}
    </div>
</div>