import {
    FC,
    useEffect,
    useState,
    memo,
    useContext,
} from 'react'
import RingLight from '@components/ringLight'
import { useWheelAngleStore } from '@store/globalStore'
import { AxesContext } from '@context/axesContext'

const RingLightPage: FC<any> = memo(() => {
    const wheelAngle = useWheelAngleStore((state) => state.wheelAngle);
    useEffect(() => {
        console.log('wheelAngle change', wheelAngle, window.dvmHandler.getWheelAngle())
    })
    // const [progress, setProgress] = useState(0)
    // const {
    //     axesValue,
    //     clushHeight,
    //     brakeHeight,
    //     throttleHeight,
    //     handbrakeHeight,
    //     wheelPedalLeft,
    //     wheelPedalRight
    // } = useContext(AxesContext)
    // const [wheelAngle, updateWheelAngle] = useState(window.dvmHandler.getWheelAngle())
    // console.log('useContext(AxesContext)', axesValue,
    // clushHeight,
    // brakeHeight,
    // throttleHeight,
    // handbrakeHeight,
    // wheelPedalLeft,
    // wheelPedalRight)
    // useEffect(() => {
    //     // setInterval(() => {
    //     //     setProgress((prev) => {
    //     //         if(prev < 100) return prev + 10;
    //     //         return 100
    //     //     })
    //     // }, 1000)
    //     console.log('useEffect--onWheelAngleChange', wheelAngle)
    //     window.dvmHandler.onWheelAngleChange((e, v) => {
    //         updateWheelAngle(v)
    //         // setWheelAngle(v);
    //         console.log('updateWheelAngle', v)
    //     });
    // }, [])
    return (
        <div style={{
            "width": "100vw",
            "height": "100vh",
            "position": "fixed",
            "left": "0",
            "top": "0",
            "background": "#dedede"
        }}>
            {/* <RingLight progress={wheelAngle >= 0 && wheelAngle / (360 / 2)}/> */}
            <RingLight progress={wheelAngle / (360 / 2)}/>
            {wheelAngle}
        </div>
    )
});

export default RingLightPage;