import React from "react"
import {
    EuiFlexGroup,
    EuiFlexItem,
    EuiPage, EuiPageBody, EuiPageContent
} from "@elastic/eui"
import styled from "styled-components"

const StyledEuiPage = styled(EuiPage)`
    flex: 1;
`
const StyledEuiPageContent = styled(EuiPageContent)`
    border-radius: 50%;
`

export default function LandingPage(props) {
    return (
        <StyledEuiPage>
            <EuiPageBody component="section">
                <EuiFlexGroup>
                    <EuiFlexItem>
                        <StyledEuiPageContent horizontalPosition="center" verticalPosition="center">
                            
                        </StyledEuiPageContent>
                    </EuiFlexItem>
                </EuiFlexGroup>
            </EuiPageBody>
        </StyledEuiPage>
    )
}