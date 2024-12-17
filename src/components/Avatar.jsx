export const Avatar = ({ username, image }) => <div class='avatar'>
    {image ? <img src={image} /> : username?.substr(0, 1)}
</div>