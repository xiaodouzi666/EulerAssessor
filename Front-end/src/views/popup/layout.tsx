import { FC } from 'react'
import { Outlet } from 'react-router-dom'
import {
    makeStyles,
} from '@fluentui/react-components';

const useStyles = makeStyles({
    layout: {
        '-webkit-app-region': 'drag',
        'height': '20px'
    }
})

const Layout: FC<any> = () => {
    const classes = useStyles()

    return (
        <div className={classes.layout}>{ <Outlet />}</div>
    )
}

export default Layout;
