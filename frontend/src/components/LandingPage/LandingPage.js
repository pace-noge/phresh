import React from "react"
import {
    EuiFlexGroup,
    EuiFlexItem,
    EuiPage, EuiPageBody, EuiPageContent, EuiPageContentBody
} from "@elastic/eui"
import { Carousel, CarouselTitle } from "../../components"
import { useCarousel } from "../../hooks/useCarousel"
import wearMask from "../../assets/img/wearMask.svg"
import bathRoom from "../../assets/img/bathRoom.svg"
import bedRoom from "../../assets/img/bedRoom.svg"
import kitchen from "../../assets/img/kitchen.svg"
import readingRoom from "../../assets/img/readingRoom.svg"
import sweetHome from "../../assets/img/sweetHome.svg"
import tvRoom from "../../assets/img/tvRoom.svg"
import car from "../../assets/img/car.svg"
import wfh from "../../assets/img/wfh.svg"
import sanitizer from "../../assets/img/sanitizer.svg"
import styled from "styled-components"

const StyledEuiPage = styled(EuiPage)`
    flex: 1;
    padding-bottom: 5rem;
`
const LandingTitle = styled.h1`
    font-size: 3.5rem;
    margin: 2rem 0;
`
const StyledEuiPageContent = styled(EuiPageContent)`
    border-radius: 50%;
`
const StyledEuiPageContentBody = styled(EuiPageContentBody)`
    max-width: 400px;
    max-height: 400px;

    & > img {
        width: 100%;
        border-radius: 50%;
    }
`
const carouselItems = [
    { label: "bath room", content: <img src={bathRoom} alt="bath" /> },
    { label: "bed room", content: <img src={bedRoom} alt="bed" />},
    { label: "vehicle", content: <img src={car} alt="vehicle" /> },
    { label: "kitchen", content: <img src={kitchen} alt="kitchen" /> },
    { label: "reading room", content: <img src={readingRoom} alt="reading" /> },
    { label: "house", content: <img src={sweetHome} alt="home" /> },
    { label: "tv room", content: <img src={tvRoom} alt="tv" /> },
    { label: "table", content: <img src={wfh} alt="working" /> },
    { label: "self", content: <img src={sanitizer} alt="sanitizer" /> },
]



export default function LandingPage(props) {
    const { current } = useCarousel(carouselItems, 3000)
    return (
        <StyledEuiPage>
            <EuiPageBody component="section">
                <EuiFlexGroup direction="column" alignItems="center">
                    <EuiFlexItem>
                        <LandingTitle>Phresh Cleaners</LandingTitle>
                    </EuiFlexItem>
                    <EuiFlexItem>
                        <CarouselTitle items={carouselItems} current={current}/>
                    </EuiFlexItem>
                </EuiFlexGroup>

                <EuiFlexGroup direction="rowReverse">
                    <EuiFlexItem>
                        <Carousel items={carouselItems} current={current}/>
                    </EuiFlexItem>

                    <EuiFlexItem>
                        <StyledEuiPageContent horizontalPosition="center" verticalPosition="center">
                            <StyledEuiPageContentBody>
                                <img src={wearMask} alt="wear mask" />
                            </StyledEuiPageContentBody>
                        </StyledEuiPageContent>
                    </EuiFlexItem>
                </EuiFlexGroup>
            </EuiPageBody>
        </StyledEuiPage>
    )
}